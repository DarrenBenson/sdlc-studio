#!/usr/bin/env python3
"""SDLC Studio status transition.

`transition --id <ID> --status <new>` performs the one mechanical write-side cascade
that was still hand-driven: set an artifact's `Status` field, sync its index row and the
summary counts, and (for a story) tick/untick its checkbox in the parent epic's Story
Breakdown. Deterministic once the new status is chosen - it reuses the validated
`reconcile.apply_type` to bring the index into line with the file, so there is no
bespoke index-row editing.

Subcommand:
  set  Transition one artifact to a new status and cascade the index/epic updates.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md, tiers  # noqa: E402
import reconcile  # noqa: E402  (sibling - reuse the tested index-row + count sync)

# Statuses that mean "complete" for the epic-breakdown checkbox (a story is ticked).
_STORY_TICKED = {"Done", "Won't Implement", "Deferred", "Superseded"}
_REPORT_REL = "sdlc-studio/.local/verify-report.json"

# Verification-depth tiers, weakest first (reference-test-best-practices.md).
_TIERS = {"smoke": 0, "functional": 1, "conversational": 2, "soak": 3, "live": 4}
_TARGET_RE = re.compile(r"^\s*-\s*\*\*Verification target:\*\*\s*`?(\w+)`?", re.M)


def _depth_token(text: str) -> str | None:
    """The leading tier token of the `Verification depth` field (decorations like
    `functional (unit)` are fine), or None when the field is absent/unparseable."""
    raw = (sdlc_md.extract_field(text, "Verification depth") or "").strip()
    token = raw.split()[0].lower().strip("`") if raw else ""
    return token if token in _TIERS else None


def _bug_depth_gate(text: str, target_canon: str | None) -> str | None:
    """Block reason when a bug transition under-shoots its verification-depth tier.

    Fixed requires `functional`+; Verified claims the higher-tier proof landed,
    so it requires a tier ABOVE functional (conversational/soak/live); Closed
    on a production-affecting bug requires `soak`+. A missing/unparseable depth
    on a gated transition is refused, never treated as satisfied (fail loud).
    The non-production Close path is unchanged, and a project that never
    promotes to Verified is unaffected."""
    if target_canon not in ("Fixed", "Verified", "Closed"):
        return None
    if target_canon == "Closed":
        prod_raw = (sdlc_md.extract_field(text, "Production-affecting") or "").strip()
        # leading-token match, mirroring the depth field: `yes (checkout path)` is
        # still yes - a decorated flag must never silently switch the soak gate OFF.
        prod_tok = prod_raw.split()[0].rstrip(":,;-").lower() if prod_raw else ""
        if prod_tok not in ("yes", "true"):
            return None
    required = {"Fixed": "functional", "Verified": "conversational",
                "Closed": "soak"}[target_canon]
    token = _depth_token(text)
    if token is None:
        return (f"no parseable `Verification depth` field; {target_canon} requires "
                f"`{required}`+ - record the verified tier "
                f"(see reference-test-best-practices.md#verification-depth-tiers)")
    if _TIERS[token] < _TIERS[required]:
        if target_canon == "Verified":
            return (f"depth is `{token}`; Verified claims a proof ABOVE the "
                    f"functional tier (conversational/soak/live) - run that "
                    f"verification, then set the depth, or stay at Fixed")
        return (f"depth is `{token}`; {target_canon} requires `{required}`+ - run the "
                f"verification that tier demands, then set the depth")
    return None


def _story_target_parity(text: str) -> str | None:
    """Advisory: Done should not out-run a declared AC `Verification target` above
    `functional` unless a story-level depth at/above it is recorded."""
    targets = [t.lower() for t in _TARGET_RE.findall(text) if t.lower() in _TIERS]
    if not targets:
        return None
    top = max(targets, key=lambda t: _TIERS[t])
    if _TIERS[top] <= _TIERS["functional"]:
        return None
    token = _depth_token(text)
    if token and _TIERS[token] >= _TIERS[top]:
        return None
    return (f"an AC declares Verification target `{top}` but the recorded depth is "
            f"`{token or 'unrecorded'}` - Done should not out-run the target")


def _iso_to_epoch(value) -> float | None:
    """Parse a verify-report timestamp to a UTC epoch, or None.

    Any ISO-8601 stamp carrying an explicit UTC offset, via the one shared reader."""
    if not value:
        return None
    # The SHARED reader. This carried its own `%Y-%m-%dT%H:%M:%SZ` pattern, so the
    # offset-bearing stamps the standard library writes - and which are live in this tree -
    # were refused here while telemetry accepted them. One rule, three implementations, two
    # of them wrong.
    parsed = sdlc_md.parse_iso8601(value)
    return None if parsed is None else parsed.timestamp()


def _story_has_executable_acs(text: str) -> bool:
    """True if the story declares any non-manual `Verify:` line (an executable AC). A story
    with only `manual` ACs (or none) has nothing the deterministic gate can check."""
    for line in text.splitlines():
        m = sdlc_md.VERIFY_RE.match(line)
        if m and m.group(2).strip().split(None, 1)[0].lower() not in ("manual", "manually"):
            return True
    return False


def _acs_missing_evidence(text: str) -> tuple[list[str], list[str], str | None]:
    """The ACs no deterministic verifier can speak for, split by WHY, and carrying no recorded
    passing human verdict: (declared manual, no `Verify:` line at all, error).

    The third element is None on a healthy parse and a short description of the failure when the
    ACs could not be read at all. It exists because the first two CANNOT express that difference:
    two empty lists are exactly what a fully-evidenced story looks like, so returning them on an
    import or parse failure told the caller "nothing is owed" when the truth was "nothing was
    looked at" - and the caller waved the story to Done.

    Manual ACs are the ones the deterministic gate CANNOT evaluate - a human observes the
    outcome. The gate cannot check the outcome, but it can require the EVIDENCE that a human did:
    a `**Verified:**` marker on each. `verify_ac` never stamps a manual AC (it counts and skips
    it), so this marker is only ever added deliberately - it cannot be auto-satisfied by running
    the verifier.

    An AC with NO `Verify:` line is the same fact stated by omission, and it used to be the
    cheaper one: it was waved through while the honestly-declared `manual` beside it was blocked,
    so silence was the fastest route to Done. It is held to the same evidence, which also puts
    this gate back in step with the release lane (`gate.py._verify_acs` already refuses an
    unspecified AC and names it).
    """
    try:
        import verify_ac  # noqa: PLC0415 - sibling; imports only sdlc_md, no cycle
        blocks = verify_ac.parse_story(text)
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        # Fail LOUD. The previous `return []` was indistinguishable from a clean bill of health,
        # so the one condition under which the gate was least able to judge - broken tooling or
        # an unreadable story - was the one condition under which it approved everything.
        return [], [], f"{type(exc).__name__}: {exc}"
    bare_manual: list[str] = []
    bare_unspecified: list[str] = []
    for b in blocks:
        toks = (b.verifier or "").strip().split(None, 1)
        # Only a PASSING human verdict is evidence. `no` records the human saw it fail, `stale`
        # that the evidence is out of date, and a missing marker that no one looked - all three are
        # "not verified" and must block, symmetric with the executable path (which blocks a red or
        # stale verifier result). Accepting any-marker-present would let one `Verified: no` line
        # reopen exactly the bypass this closes.
        if not toks:
            # A bare AC is UNSPECIFIED, and a `Verified:` marker does not make it specified. The
            # release lane counts it unspecified regardless of any marker and refuses on it, so
            # exempting it here made the two gates disagree about the same file - a story closed
            # Done all sprint and failing only at tag time, which is the defect this closes.
            bare_unspecified.append(b.ac_id)
            continue
        if b.verified_state == "yes":
            continue
        if toks[0].lower() in ("manual", "manually"):
            bare_manual.append(b.ac_id)
    return bare_manual, bare_unspecified, None


def _two_role_gate(root: Path, rid: str) -> str | None:
    """The two-role bar, asked by the verb that WRITES `Status: Done`. Block reason, or None.

    The Definition of Done states this clause and `conformance.py` implements it properly - but
    conformance is a lane that runs later, over a status a different tool has already written.
    Nothing at the moment of the write said no, so a unit could be moved to Done with no
    independent review whatsoever and the only trace was a report somebody had to run and read.
    That is the mechanism behind every Done story carrying no independent verdict: they did not
    slip past a gate, the gate they are said to have passed was never asked. The count of 25
    that circulated with this bug is NOT supported by the tree - a claims-lens census found 21
    units with neither a per-unit independent verdict nor sprint cover, all of them pre-cutoff,
    and none in the D0074 cohort failing the critiqued stage.

    Uses `conformance`'s VOCABULARY - the `HALF_*` constants the lane reports - so the verb and
    the lane name the same halves. It does NOT route its two `critic` reads through
    `conformance.critiqued_unmet`, for a mechanical reason recorded at the call site: callers
    that stub `critic` load it as a separate module object, so a call made through conformance
    sees the real one and silently disagrees with the caller's fixture. That is the defect one rung down that this
    same sprint fixed for the independence predicates. Forward-only: a project with no
    `review.two_role_after`, and any unit at or below the cutoff, is unaffected byte-for-byte.

    Fails CLOSED on an unreadable config or ledger. A gate that cannot establish the bar has not
    cleared it, and this gate exists precisely because silence was being read as a pass.
    """
    # THE CONFIG IS READ FIRST, AND ITS FAILURE IS FATAL. `project_override` swallows every
    # config fault by design and hands back the default, so an unreadable `.config.yaml` made
    # the cutoff None, `two_role_applies_to` False, and this gate returned before it ever
    # touched a ledger - a unit past the cutoff reached Done, exit 0, over malformed YAML, a
    # tab-indented file, non-UTF-8 bytes, a `.config.yaml` that is a directory, or simply no
    # PyYAML. That is the gate's own docstring principle - silence read as a pass - reproduced
    # one layer up in the gate written to close it. A project that DECLARES the rule and then
    # cannot be read has not waived it.
    cfg = root / "sdlc-studio" / ".config.yaml"
    if cfg.exists() and sdlc_md.config_unparseable(cfg):
        return (f"`{cfg.name}` exists but could not be parsed, so the two-role cutoff is "
                f"UNKNOWN - an unreadable bar is not a passed one. Fix the config, then retry; "
                f"`--force` overrides")
    try:
        import conformance  # noqa: PLC0415 - deferred; transition is on every hot path
        cutoff = sdlc_md.parse_cutoff(sdlc_md.project_override(root, "review.two_role_after"))
        if not conformance.two_role_applies_to(rid, cutoff):
            return None
        # Genuinely delegated now - the predicate AND the vocabulary, which the first version
        # claimed and did not do: it re-implemented both halves inline with its own strings and
        # omitted the verdict half entirely, so it was WEAKER than the lane it was meant to
        # front. A story could reach Done with no independent APPROVE recorded and conformance
        # would then mark it non-conformant: two answers to one question.
        # The project's Definition of Done can stand EITHER half down, and the lane honours
        # that: a DoD without `review.critic-approve` downgrades the verdict half to human
        # judgement, and one without `review.two-role` stands the sign-off requirement down
        # even under the cutoff. A verb that ignored those would refuse work the lane accepts -
        # the same two-answers-to-one-question defect as being weaker than it, pointing the
        # other way.
        story_dod = sdlc_md.dor_dod_level_checks(root, "done", "story")
        critic_required = story_dod is None or "review.critic-approve" in story_dod
        if story_dod is not None and "review.two-role" not in story_dod:
            cutoff = None
        # TWO-ROLE halves only: this gate's bar is the Definition of Done's two-role clause,
        # which is what BG0417 is about. The verdict half belongs to the `critiqued` stage and
        # conformance enforces it there; demanding it here refused work the lane accepts.
        #
        # The VOCABULARY is conformance's - `HALF_EVIDENCE`, `HALF_SIGNOFF`, the constants the
        # lane reports - so the verb and the lane name the same halves and a rename moves both.
        # The two `critic` calls are made HERE rather than through `conformance.critiqued_unmet`
        # for a mechanical reason, not a stylistic one: callers that stub `critic` load it as a
        # separate module object, so a call routed through conformance sees the REAL critic and
        # silently disagrees with the caller's fixture. Routing it there made four close-preflight
        # tests refuse work they had approved for a year. The residual duplication is two lines
        # and is filed rather than hidden.
        del critic_required                # the verdict half is not this gate's to demand
        import critic  # noqa: PLC0415
        sprint_covers = critic.sprint_covers_independently(
            root, rid, critic.sprint_review_for(root, rid))
        unmet = []
        if not (bool(critic.evidence_for(root, rid)) or sprint_covers):
            unmet.append(conformance.HALF_EVIDENCE)
        if not critic.is_independent_signoff(root, rid, critic.signoff_for(root, rid)):
            unmet.append(conformance.HALF_SIGNOFF)
    except Exception as exc:  # noqa: BLE001 - see the docstring: unreadable is not cleared
        return (f"the two-role gate could not be established ({type(exc).__name__}: {exc}) - "
                f"an unreadable bar is not a passed one")
    if not unmet:
        return None
    # Every unmet half in ONE refusal, named separately: an absent adversarial pass, an absent
    # verdict and an absent sign-off need different actions from different people, and a
    # round-trip per half is the cost the ladder elsewhere in this module already avoids.
    remedy = {conformance.HALF_VERDICT: "record an independent critic APPROVE (`critic.py "
                                        "record`, reviewer != author)",
              conformance.HALF_EVIDENCE: "record the adversarial pass as evidence (`critic.py "
                                         "evidence --from-verdict`, or a sprint-level review)",
              conformance.HALF_SIGNOFF: "record an independent reviewer-of-record sign-off "
                                        "(`critic.py signoff`, a principal the author does "
                                        "not control)"}
    return (f"{rid} is past `review.two_role_after` and {len(unmet)} half/halves of the review "
            f"bar are unmet - " + "; and ".join(f"{h}: {remedy.get(h, 'unmet')}" for h in unmet))


def _done_verify_gate(root: Path, path: Path, text: str) -> str | None:
    """Definition-of-Done safety net on the hand-driven path. A story may not reach
    Done with executable ACs that are red or never run - the 0/7 a hand-driving agent shipped.
    Returns a block reason, or None to allow. A green report passes. The hard gate is the one
    deterministic fact - the verifier result; critic semantic findings stay advisory (handled
    elsewhere).

    A manual AC is not exempt from all scrutiny: the gate cannot judge the OUTCOME a human must
    observe, but it requires the EVIDENCE that a human did and it PASSED - a `**Verified:** yes`
    marker. Without a passing verdict (`no`, `stale`, or nothing at all), `manual` meant "nothing
    checks this", and the more irreversible the work the less it was gated. This runs first, so an
    all-manual story is no longer waved through with nothing looked at.

    An AC carrying no `Verify:` line at all is held to the same evidence, for the same reason and
    with no discount for saying nothing: waving it through made omission strictly cheaper than
    honest declaration, and it disagreed with the release lane, which refuses an unspecified AC -
    so a story closed Done all sprint failed only at tag time."""
    bare_manual, bare_unspecified, evidence_error = _acs_missing_evidence(text)
    if evidence_error is not None:
        # Broken tooling is not a passed gate. Refuse and name the failure, so the actor repairs
        # the story or the environment rather than being handed a Done nothing checked.
        return (f"the manual-evidence check could not run ({evidence_error}) - an unreadable "
                f"story or a broken `verify_ac` import is not a passed gate. Fix that, then "
                f"retry; `--force` overrides deliberately")
    # Both are reported in ONE refusal: fixing one and being refused for the other next attempt
    # is the round-trip-per-gate cost the ladder above already avoids.
    parts = []
    if bare_manual:
        parts.append(f"manual acceptance criteria ({', '.join(bare_manual)}) reached Done with no "
                     f"recorded PASSING verification - add a `**Verified:** yes` marker (when "
                     f"observed, by whom) to each, or make the criterion executable. A "
                     f"`no`/`stale` marker blocks like a red verifier does")
    if bare_unspecified:
        parts.append(f"acceptance criteria ({', '.join(bare_unspecified)}) carry no `Verify:` "
                     f"line at all - an omitted verifier is not a passed one. Author one, or "
                     f"declare `- **Verify:** manual <what a human checks>` and record a "
                     f"`**Verified:** yes` marker; omission buys no discount over declaring it")
    if parts:
        return "; and ".join(parts)
    if not _story_has_executable_acs(text):
        return None  # nothing executable to verify; manual evidence (if any) is present
    # The story-level Definition of Done, when the project declares one, decides whether
    # this check enforces: a DoD whose story level does not tag `story.verify-ac` has
    # downgraded AC verification to human judgement (a visible edit to the document, and
    # noted here so the stand-down is never silent). Absent document = today's behaviour.
    dod = sdlc_md.dor_dod_level_checks(root, "done", "story")
    if dod is not None and "story.verify-ac" not in dod:
        print("note: story.verify-ac is downgraded to human-judged by "
              "definition-of-done.md - the AC-verify Done gate stands down", file=sys.stderr)
        return None
    report_path = root / _REPORT_REL
    if not report_path.exists():
        return "this story declares executable ACs but they were never verified - run `verify_ac`"
    try:
        entry = (json.loads(report_path.read_text(encoding="utf-8")).get("stories", {}) or {}).get(path.stem)
    except (ValueError, OSError):
        entry = None
    if entry is None:
        return "this story is not in the verify-report - run `verify_ac` before Done"
    if entry.get("failed", 0) or entry.get("stale", 0):
        fails = ", ".join(f.get("ac", "?") for f in entry.get("failures", [])) or "stale AC(s)"
        return f"AC verification is red ({fails}) - fix or re-verify before Done"
    # A green entry can still be STALE: the story may have been edited since it was verified
    # (a changed Verify line, or a new AC). A merged report carries the old green forever, so
    # the entry alone is not proof the CURRENT story passes.
    # Prefer a CONTENT fingerprint over mtime. mtime answers "was the file touched", not
    # "did what we verified change": a Status transition, a Revision History row, or
    # verify_ac's own `**Verified:**` stamp all bump mtime while the ACs and their
    # verifiers are untouched, so a correct green was rejected as stale. Reports written
    # before the fingerprint existed carry none - those still fall back to mtime rather
    # than silently passing.
    recorded_fp = entry.get("ac_fingerprint")
    if recorded_fp:
        try:
            import verify_ac  # sibling; imports only sdlc_md, no cycle
            current_fp = verify_ac.ac_fingerprint(text)
        except Exception:  # noqa: BLE001 - a parse hiccup must not mask the gate; fall back to mtime
            current_fp = None
        if current_fp is not None:
            if current_fp != recorded_fp:
                return ("this story's acceptance criteria changed after it was last verified "
                        "- re-run `verify_ac` before Done")
            return None  # ACs are byte-identical to what passed; mtime is noise
    verified_at = _iso_to_epoch(entry.get("verified_at"))
    try:
        story_mtime = path.stat().st_mtime
    except OSError:
        story_mtime = None
    if verified_at is not None and story_mtime is not None and story_mtime > verified_at + 2:
        return "this story was edited after it was last verified - re-run `verify_ac` before Done"
    reported_acs = entry.get("ac_count")
    if reported_acs is not None:
        try:
            import verify_ac  # sibling; imports only sdlc_md, no cycle
            current_acs = len(verify_ac.parse_story(text))
        except Exception:  # noqa: BLE001 - a parse hiccup must not mask the gate; skip this leg
            current_acs = None
        if current_acs is not None and current_acs != reported_acs:
            return (f"the story now has {current_acs} AC(s) but the verify-report covers "
                    f"{reported_acs} - re-run `verify_ac` before Done")
    return None


# The status cell is read as free text, not a closed vocabulary. Real decision rows carry
# their reasoning inline - `Open - the mechanism detail for the blocking lane`, `Resolved:
# option D (...)` - so a reader demanding the bare word misses a genuinely Open row and
# reports the file clean. A false negative in the gate is worse than the prose rule it
# replaces, because it also looks like proof.
#
# Every structural assumption here has been a false negative at least once, so each is now
# as loose as it can be while still discriminating: the row may have ANY column count (the
# status is the LAST cell), a cell may contain an escaped pipe, and the section heading may
# be at any level. The first version fixed all three and let four real shapes through.
_DECISION_ROW_RE = re.compile(r"^\s*\|\s*(D\d+)\s*\|(.+)\|\s*$")
#: A cell separator is an UNESCAPED pipe; `\|` is a literal pipe inside a cell.
_DECISION_PIPE_RE = re.compile(r"(?<!\\)\|")
#: Leading tokens that mean "not settled". Anything else - Closed, Resolved, Superseded, a
#: prose verdict - is a decision that was taken, because the register records what was
#: decided rather than a fixed vocabulary.
_UNSETTLED = ("open", "unresolved", "undecided", "tbd", "pending")
#: An ATX heading: one to six hashes followed by whitespace. Anything else that
#: merely begins with `#` - a shell comment, an issue reference - is not a heading.
_ATX_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")


def _rfc_open_decisions(text: str) -> list[str]:
    """The decision numbers still Open in an RFC's decision table (rows only).

    `_rfc_open_decisions_detail` is the same reading plus WHICH path produced it. A caller
    that reports the rows to a human wants the detail form: the two paths differ in what a
    row means, so a message that cannot say which one ran cannot be acted on correctly.
    """
    return _rfc_open_decisions_detail(text)[0]


def _rfc_open_decisions_detail(text: str) -> tuple[list[str], bool]:
    """The rows, and True when the FAIL-CLOSED fallback produced them.

    The decision numbers still Open in an RFC's decision table.

    Rows are normally read only inside the decisions section: a `| D1 | ... | Open |` line in
    a Summary or an appendix is prose, not the register the accept step is about.

    ONE EXCEPTION, and it is not a corner case. If the scan ends inside an unterminated fence
    the section boundaries could not be established, and this falls back to
    `_rfc_open_decisions_unstructured`, which reads every unsettled row ANYWHERE in the file -
    Summary and appendix included. So the guarantee above holds for the ordinary path only,
    and the return value can name a row outside the register. Stated here because the previous
    wording promised the narrow reading unconditionally while the fallback had already broken
    it, and a caller trusting the docstring would mis-read the result.
    """
    open_rows: list[str] = []
    in_section = False
    fence = None          # (char, length) of the OPEN fence, or None
    for line in text.splitlines():
        # A fenced block holds no headings and no decision rows, so it is skipped. The rule
        # is CommonMark's, not a toggle: a fence opens on 3+ of ` or ~ and closes only on the
        # SAME character at that length or longer. A naive `not in_fence` toggle counted the
        # inner ```bash of a ````markdown block as a delimiter and ended the file inside a
        # fence, hiding the whole section - a wider bypass than the one it was fixing.
        stripped = line.lstrip()
        marker = "`" if stripped.startswith("```") else ("~" if stripped.startswith("~~~") else None)
        if marker:
            run = len(stripped) - len(stripped.lstrip(marker))
            if fence is None:
                fence = (marker, run)
                continue
            if marker == fence[0] and run >= fence[1]:
                fence = None
                continue
            # a shorter or different fence inside an open one is CONTENT
        if fence is not None:
            continue
        # An ATX heading is one to six hashes THEN whitespace. `#42` and `#!/bin/sh` are
        # not headings, and neither ends a section.
        if _ATX_HEADING_RE.match(line):
            in_section = "decision" in line.lower()
            continue
        if not in_section:
            continue
        m = _DECISION_ROW_RE.match(line)
        if not m:
            continue
        # The status is the LAST cell, whatever the column count, split on unescaped pipes.
        cells = [c.strip() for c in _DECISION_PIPE_RE.split(m.group(2))]
        status = cells[-1].lower() if cells else ""
        # Judged on the LEADING token, so an annotated cell still counts while one that
        # merely mentions the word ('Closed - was open until the 07-19 review') does not.
        if any(status.startswith(word) for word in _UNSETTLED):
            open_rows.append(m.group(1))
    if fence is not None:
        # The scan ended inside an unterminated fence, so anything after it was skipped and
        # THIS READING IS INCOMPLETE - whether or not it happened to find something first.
        # Fail CLOSED by re-reading the document with every structural rule dropped. A false
        # positive here asks a human to look; a false negative silently accepts an RFC with
        # open decisions, and that is the failure this gate exists for.
        #
        # The condition was `fence is not None and not open_rows`, which fired only on an
        # EMPTY read. With one open row before the broken fence and another after it, the
        # first was found, the re-scan was skipped, and the caller received a list missing
        # every row the fence hid - reported to the operator as the complete set.
        # The unstructured read drops both structural rules, so it is a superset of this one:
        # re-scanning unconditionally can only add rows, never lose them.
        return _rfc_open_decisions_unstructured(text), True
    return open_rows, False


def _rfc_open_decisions_unstructured(text: str) -> list[str]:
    """Every unsettled decision row in the document, ignoring fences AND sections.

    The fail-closed path, reached only when the main scan ended inside an unterminated
    fence. It deliberately drops the section rule as well as the fence rule, because the
    two structural signals fail together: an unterminated fence means the document's
    structure cannot be trusted, and a `#` line inside that fence is exactly as likely to
    be a shell comment as a heading. An earlier version dropped only the fence rule and
    kept `in_section`, which let a `# comment` inside the broken fence end the section and
    hide every row after it - the fallback then returned "no open decisions" for the very
    document it existed to catch, so the gate advertised fail-closed and failed OPEN.

    Reading a row outside the decisions section is the intended cost, and it is paid on VALID
    documents, not only broken ones. CommonMark closes an open fence at end of document, so a
    file ending inside a fence - an appendix whose last block is never closed - is well-formed
    markdown that every parser accepts. An earlier version of this docstring claimed the
    opposite ("on a well-formed document this function never runs") and justified the cost as
    prompting someone to fix markdown that needed fixing; there may be nothing to fix, and the
    honest description is that this trades a rare false POSITIVE for the impossibility of a
    false negative. An operator facing that can record a `Decision-Override`.
    """
    open_rows: list[str] = []
    for line in text.splitlines():
        m = _DECISION_ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in _DECISION_PIPE_RE.split(m.group(2))]
        status = cells[-1].lower() if cells else ""
        if any(status.startswith(word) for word in _UNSETTLED):
            open_rows.append(m.group(1))
    return open_rows


def _rfc_accept_gate(text: str, target_canon: str | None) -> str | None:
    """Block an RFC reaching Accepted while any decision row is Open.

    `reference-rfc.md`'s accept step has always forbidden this, but only in prose, and a
    rule with no mechanism fires when somebody remembers: six RFCs reached Accepted, were
    decomposed and were delivered carrying nothing but the boilerplate Open row.

    The sanctioned escape is a RECORDED `> **Decision-Override:**` reason, not `--force`,
    matching the plan-review convention - a skip that leaves its reason in the file is
    auditable afterwards, a force flag is not.
    """
    if target_canon != "Accepted":
        return None
    still_open, from_fallback = _rfc_open_decisions_detail(text)
    if not still_open:
        return None
    override = ""
    for line in text.splitlines():
        if line.startswith("> **Decision-Override:**"):
            override = line.split("**Decision-Override:**", 1)[1].strip()
            break
    if override:
        return None
    # NAME the scan path. The fallback deliberately over-reports, and an operator who cannot
    # tell a deliberate over-report from a real open decision does one of two things: edits
    # valid markdown until the tool is satisfied, or stops believing the gate. The second is
    # worse, and neither is the operator's fault when the message withholds what it knows.
    source = (" This list came from the FAIL-CLOSED fallback: the document ends inside an "
              "unterminated fence, which is valid CommonMark, so every unsettled row ANYWHERE "
              "in the file was counted - fenced examples included. It trades a rare false "
              "positive for the impossibility of a false negative (reference-rfc.md). If every "
              "real decision is settled, close the fence or record the override."
              if from_fallback else "")
    return (f"RFC carries {len(still_open)} Open decision(s): {', '.join(still_open)} - close "
            f"each row with what was decided, or record `> **Decision-Override:** <reason>` "
            f"(--force does not bypass this: the skip must leave a reason in the file)." + source)


def _rfc_override_reason(text: str) -> str:
    """The recorded override reason, for reporting a sanctioned skip back to the caller."""
    for line in text.splitlines():
        if line.startswith("> **Decision-Override:**"):
            return line.split("**Decision-Override:**", 1)[1].strip()
    return ""


def _request_terminal_gate(root: Path, type_: str, artifact_id: str,
                           target_canon: str | None) -> str | None:
    """A DISCOVERY item (CR/RFC/Issue) may not reach its SUCCESSFUL terminal by assertion (G2). A
    CR is Complete only when every story and epic it produced is resolved (in a terminal state);
    an RFC is Accepted only when every CR it produced is resolved; an Issue is Resolved only when
    every bug it was triaged into is resolved. "Resolved" is terminal, not strictly Done: a child
    legitimately dropped (a Won't-Implement story, a Won't-Fix bug, a Rejected child CR) does not
    force the parent onto --force. A childless discovery item cannot be successfully terminal - it
    produced nothing, so it delivered nothing.

    Scoped to the successful terminal (Complete for a CR, Accepted for an RFC, Resolved for an
    Issue): a discovery item the team decides NOT to build is still closable as Rejected /
    Superseded / Withdrawn / Won't Fix / Closed without children, because that closure asserts no
    delivery. Returns a block reason, or None to allow. Overridable with --force, like the other
    close gates, but the sanctioned path is to finish or close the children first."""
    if not sdlc_md.is_discovery(type_):
        return None
    if target_canon != sdlc_md.default_terminal_status(type_):
        return None  # Rejected / Superseded / Withdrawn: closing without a delivery claim
    children = sdlc_md.children_of(root, artifact_id)
    if not children:
        return (f"{artifact_id} has no children - a request delivers nothing until it is "
                f"decomposed. Break it into the stories/epics that deliver it (write each "
                f"child's `Parent:` and this request's `Decomposed-into:`), or close it as "
                f"Rejected/Superseded if it is not going ahead")
    unfinished: list[str] = []
    for cid, ctype in children:
        hit = sdlc_md.find_by_id(root, cid)
        if not hit:
            unfinished.append(f"{cid} (unresolvable)")
            continue
        cpath, real_type = hit
        cvocab = sdlc_md.status_vocab(real_type, root)
        cstatus = sdlc_md.canonical_status(
            sdlc_md.extract_field(cpath.read_text(encoding="utf-8"), "Status"), cvocab)
        if not sdlc_md.is_terminal_status(real_type, cstatus or ""):
            unfinished.append(f"{cid} ({cstatus or 'no status'})")
    if unfinished:
        return (f"{artifact_id} cannot be {target_canon}: its status is DERIVED from its "
                f"children, and {len(unfinished)} is/are not yet resolved: "
                f"{', '.join(unfinished)}. Finish or close them first")
    return None


def _find(repo_root: Path, artifact_id: str):
    """(path, type) of the artifact with this id, or (None, None). Delegates to the shared
    alias-aware `sdlc_md.find_by_id`; normalises its None to the (None, None) this call site
    unpacks."""
    return sdlc_md.find_by_id(repo_root, artifact_id) or (None, None)


def _set_field(text: str, name: str, value: str) -> tuple[str, bool]:
    """Replace a `**Name:** value` field's value in place (blockquote or inline `·`
    form), preserving the surrounding format. Returns (new_text, changed)."""
    pat = re.compile(
        rf"((?:^>?\s*|·\s*)\*\*{re.escape(name)}:\*\*\s*)(.+?)(\s*(?=·|\s\*\*[^*\n]+:\*\*|$))",
        re.M)
    new_text, n = pat.subn(lambda m: m.group(1) + value + m.group(3), text, count=1)
    return new_text, n > 0


def _insert_after_status(text: str, line: str) -> str:
    """Insert `line` immediately after the `> **Status:**` metadata line (used to add a
    field that does not yet exist, e.g. a first-time `Triaged-by`). No-op if no Status line."""
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if re.match(r">?\s*\*\*Status:\*\*", ln):
            lines.insert(i + 1, line if line.endswith("\n") else line + "\n")
            return "".join(lines)
    return text


def _upsert_field(text: str, name: str, value: str) -> str:
    """Set `**Name:** value` in place, or insert it after Status when the field is absent.

    The single writer of a metadata line, and so the single place the line-break refusal
    belongs - the analogue of the row writer's cell guard. A name or value carrying a line
    break escapes the line it is written into, and whatever follows the break is read back as
    a metadata field of its own; a triage stamp could therefore write any field into the
    artefact it was closing, including one the file had no other way to acquire. Guarding the
    writer means every caller inherits the refusal instead of each one remembering it - which
    `annotate` did and the triage stamps did not.
    """
    sdlc_md.require_single_line("metadata field name", name)
    sdlc_md.require_single_line(f"metadata field {name!r}", value)
    new_text, changed = _set_field(text, name, value)
    return new_text if changed else _insert_after_status(text, f"> **{name}:** {value}")


# Fields annotate must NEVER touch: they are gate-protected, index-backed, or a cross-script
# security control, and a stamp verb that could rewrite them would be a sanctioned, exit-0
# bypass. `status`/`triaged-by`/`triage-severity` gate the transition ladder;
# `provenance` is the verify_ac shell-execution boundary - annotate clearing an
# `external` stamp would re-enable shell on untrusted content. The only
# provenance mutation that matters (external -> non-external) is always the dangerous
# direction, and there is no legitimate post-creation re-stamp. `template` gates the
# promotion ladder: annotating it to `full` cleared the planning gate AND its conformance
# backstop in one exit-0 line, with no waiver and no record - a documented skip printing
# green over the sections the tier deferred. The tier is changed by `artifact.py promote`,
# which ADDS those sections; there is no legitimate way to change it without them.
# Case-insensitive.
_ANNOTATE_DENYLIST = {"status", "triaged-by", "triage-severity", "provenance", "template"}
# The remedy named in the refusal, per denied field - so a refusal points somewhere.
_ANNOTATE_REMEDY = {
    "template": "the tier is changed by `artifact.py promote --id <id> --to full`, which adds "
                "the deferred sections; a stamp without them is a claim, not the work",
}


def annotate(repo_root: Path | str, artifact_id: str, field: str, value: str) -> dict:
    """Deterministically set/update one metadata field on an artifact (the stamp verb the
    unit-close ceremony was missing - depth, evidence and similar fields no longer need a
    hand edit). Index-untouched: metadata fields are not index columns. Fails loud on an
    unresolvable id, a gate-protected field, an injection-shaped value, or a file with no
    metadata block to anchor to."""
    root = Path(repo_root)
    key = field.strip().lower()
    if key in _ANNOTATE_DENYLIST:
        remedy = _ANNOTATE_REMEDY.get(key, "status and triage records go through `transition "
                                            "set` so their gates run")
        raise ValueError(f"annotate refuses the gate-protected field {field!r}: {remedy}")
    # A line-broken field/value is refused by `_upsert_field` below - the one writer of a
    # metadata line, and so the one place that rule lives. This verb keeps no copy of it: a
    # caller-side copy is how the triage stamps came to be written by a writer that did not
    # refuse them.
    path, type_ = _find(root, artifact_id)
    if path is None:
        raise FileNotFoundError(f"cannot annotate {artifact_id}: artifact not found")
    text = path.read_text(encoding="utf-8")
    new_text = _upsert_field(text, field, value)
    if new_text == text and sdlc_md.extract_field(text, field) != value:
        # nothing matched AND nothing could be inserted: the file has no Status anchor
        raise ValueError(f"cannot annotate {artifact_id}: no `> **Status:**` metadata block "
                         "to anchor the field to - not a structured artifact")
    if new_text != text:
        sdlc_md.atomic_write(path, new_text)
    return {"id": artifact_id, "type": type_, "field": field, "value": value,
            "changed": new_text != text, "path": str(path)}


_REVISION_HEAD_RE = re.compile(r"^##\s+Revision History\s*$", re.MULTILINE)


def append_revision_row(text: str, date: str, author: str, note: str) -> tuple[str, bool]:
    """`text` with one dated `| date | author | note |` row appended after the last row of
    its `## Revision History` table, or `(text, False)` when there is no such section or the
    section carries no table.

    The shared revision-log writer the deterministic verbs use to leave an auditable trail of
    a mechanical change (a retitle records the previous title through it), so the row shape and
    the cell-escaping live in one place rather than being re-hand-rolled per caller. The three
    cells go through `sdlc_md.join_row`, which escapes a literal pipe and refuses a line break,
    so a note carrying either cannot forge a fourth column or a second row."""
    m = _REVISION_HEAD_RE.search(text)
    if not m:
        return text, False
    lines = text.splitlines()
    head_ln = text[: m.start()].count("\n")
    j = head_ln + 1
    last_row = None
    while j < len(lines):
        s = lines[j].strip()
        if s.startswith("|"):
            last_row = j
        elif s.startswith("## ") or (last_row is not None and s and not s.startswith("|")):
            break
        j += 1
    if last_row is None:
        return text, False
    lines.insert(last_row + 1, sdlc_md.join_row([date, author, note]))
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), True


def _triage_gate(root: Path, type_: str, text: str, from_canon: str | None,
                 target_canon: str | None, triaged_by: str | None) -> str | None:
    """Block reason when a v3 finding is leaving the `inbox` triage lane without a valid,
    separated `triaged_by`; None when the transition is not a triage or the gate is satisfied.
    Leaving `inbox` by ANY exit is the triage act (accept into the workflow, or reject the
    finding), so every such transition is gated - not only the canonical accept target - or an
    agent could sidestep triage by moving a finding straight to another state. Enforces CR0169
    (structured triaged_by, recorded at transition time) and CR0170 (separation of duties: the
    triager must not be the raiser). A solo human self-triage is not blocked (a lone operator
    must not deadlock) - it is left to the caller to warn, mirroring validate.py."""
    if not (type_ in sdlc_md.FINDING_TYPES and sdlc_md.is_schema_v3(root)):
        return None
    if from_canon != sdlc_md.INBOX_STATUS:  # only transitions leaving the inbox lane are triage
        return None
    raw = triaged_by or sdlc_md.extract_field(text, "Triaged-by")
    tb = sdlc_md.parse_authorship_value(raw)
    if not tb or not tb["name"]:
        return ('triage requires a structured `--triaged-by "Name; type; version"` '
                "(type is human|persona|agent) - the triaging seat must be recorded")
    if tb["type"] not in ("human", "persona", "agent"):
        return f"triaged_by type {tb['type']!r} must be one of human|persona|agent"
    raiser = sdlc_md.parse_authorship(text, "Raised-by")
    if raiser and raiser["name"]:
        same = (sdlc_md.norm_id(raiser["name"]) == sdlc_md.norm_id(tb["name"])
                and raiser["type"] == tb["type"])
        if same and tb["type"] != "human":
            return (f"triaged_by {tb['name']!r} is the raiser - a different seat must triage "
                    "(separation of duties, CR0170)")
    return None


def _cascade_epic(repo_root: Path, story_id: str, ticked: bool) -> str | None:
    """Tick/untick the story's line in its parent epic's Story Breakdown (called only on
    a real write). Returns the epic id touched, or None."""
    spath, _ = _find(repo_root, story_id)
    if spath is None:
        return None
    epic_field = sdlc_md.extract_field(spath.read_text(encoding="utf-8"), "Epic") or ""
    m = sdlc_md.ID_SEARCH_RE.search(epic_field)
    if not m:
        return None
    epath, _ = _find(repo_root, m.group(0))
    if epath is None:
        return None
    norm = sdlc_md.norm_id(story_id)
    lines = epath.read_text(encoding="utf-8").splitlines()
    changed = False
    box = "[x]" if ticked else "[ ]"
    for i, ln in enumerate(lines):
        s = ln.lstrip()
        if s.startswith(("- [ ]", "- [x]", "- [X]")) and sdlc_md.ID_SEARCH_RE.search(ln) \
                and sdlc_md.norm_id(sdlc_md.ID_SEARCH_RE.search(ln).group(0)) == norm:
            new = re.sub(r"\[[ xX]\]", box, ln, count=1)
            if new != ln:
                lines[i] = new
                changed = True
            break
    if changed:
        sdlc_md.atomic_write(epath, "\n".join(lines) + "\n")
    return m.group(0) if changed else None


_IMPL_TARGETS = {"In Progress", "Review", "Done"}


def _tier_gate(root: Path, text: str, type_: str) -> str | None:
    """Block reason when a story or epic reaches an implementation-facing status without the
    sections the full template carries.

    Keyed on the SECTIONS, not on the tier stamp: a stamp is a claim the subject can rewrite,
    and a gate that trusts one is defeated by rewriting it. `lib.tiers.promotion_deficit` owns
    the judgement (fail closed on an unknown tier; a `full` claim is checked against the
    sections; an unstamped artefact is untouched unless the project sets
    `quality.require_full_sections`).

    Fires on EVERY entry to an implementation status, not just the first: the deficit is a
    property of the file, not a one-off event, and it persists until the sections are there.
    Not bypassable with `--force`, because the sanctioned route ADDS the sections rather than
    waiving them - and `transition annotate` refuses the tier field for the same reason."""
    return tiers.promotion_deficit(text, type_, strict=tiers.require_full_sections(root))


class GateRefusal(ValueError):
    """A transition refused by the gate ladder, carrying the blocks as DATA.

    Subclasses ValueError so every existing caller and test keeps working unchanged - the
    message is identical. `blocks` exists so a reader does not have to re-parse that message:
    the ladder joins with `"; AND "` but only SOME gates suffix their reason with
    `". Override with --force"`, so splitting on the suffix merges any two adjacent gates that
    do not carry it, and leaks the delimiter into the next item when they alternate. Rebuilding
    a list from a sentence is guesswork about a format nothing pinned; passing the list is not.
    """

    def __init__(self, message: str, blocks: list[str]):
        super().__init__(message)
        self.blocks = list(blocks)


def _pre_write_gates(root, artifact_id, new_status, type_, path, text,
                     target_canon, from_canon, force, dry_run, triaged_by) -> str | None:
    """Run the ordered pre-write gates (bug-depth, depth-parity, done-verify, triage,
    plan-review). Raise ValueError on a hard block; else return the accumulated advisory
    warning (or None). Behaviour-preserving extraction of the interleaved gate ladder."""
    gate_warn = None
    # Every unmet gate is COLLECTED and reported in one refusal - refusing one requirement
    # per attempt cost an agent a round-trip per gate (three attempts to close a v3 finding).
    blocks: list[str] = []
    # These gates fire on a DRY-RUN too, for the reason the tier gate below already states: an
    # honest preflight surfaces the refusal a real run would hit. Suppressing them made the
    # dry-run report `would set BG0001 Open -> Fixed` for a transition the real run BLOCKS, so
    # the one pre-flight an agent has gave the opposite answer to the real thing. `force` is
    # still honoured, because a forced dry-run must predict what a forced real run does.
    # The criteria floor, at the VERB. BG0370 closed it at the validate layer, which the
    # pre-commit gate enforces - so a unit could not LAND at a terminal status with no
    # criteria, but `transition set` still performed the change and the refusal arrived later,
    # from a different tool, phrased as a validation error. Defence at the gate rather than at
    # the verb is weaker than the rule reads, and it leaves the working tree in the state the
    # rule forbids. The PREDICATE is validate's own, imported rather than re-derived, so the
    # two cannot disagree about what counts as a criterion.
    #
    # Only a DELIVERED-terminal status: a unit ruled `Won't Fix` or `Superseded` was never
    # built, so it owes no contract. That distinction is `sdlc_md.is_delivered_terminal`, read
    # here and by `close_owed`, rather than a second list of statuses to drift.
    if (not force and sdlc_md.executes_verifiers(type_)
            and sdlc_md.is_delivered_terminal(type_, target_canon or "")):
        try:
            import validate as _validate
            has_criteria = _validate._has_criteria(text)
        except Exception:  # noqa: BLE001 - an unimportable validator must not break the verb
            has_criteria = True
        if not has_criteria:
            blocks.append(
                f"no acceptance criteria; {target_canon} requires at least one - a unit "
                f"reaching a terminal status with nothing stating what done looks like "
                f"cannot be checked by anything downstream. Add a criterion (a `Verify:` "
                f"line makes it executable), or state the absence deliberately. "
                f"Override with --force")
        else:
            # HAVING criteria is not the same as anything speaking for them. A story is gated
            # on its executable ACs at `Done`; a bug reaching `Fixed` had no equivalent, so
            # eight terminal bugs carried 31 unticked boxes and zero `Verify:` lines and passed
            # every check. A criterion nobody ticked and nothing runs is a sentence, not an
            # oracle - and the artefact then declares itself unfinished while standing at a
            # status that says otherwise.
            #
            # EITHER satisfies it: a ticked criterion is a human saying so, an executable one
            # is the machine saying so. Demanding both would refuse the ordinary judgement call
            # a bug fix often is.
            # BUGS ONLY. A story reaching `Done` already passes the AC-verify gate, which
            # EXECUTES its criteria - a stronger oracle than either of these, and applying this
            # on top would refuse stories the stronger gate accepts while talking about "this
            # fix". The hole this closes is the one bugs had: `Fixed` with no equivalent.
            # SCOPED to the criteria. Searching the whole artefact made the gate answerable
            # by prose it never asked about: a `- [x] I reproduced it` in Steps to Reproduce,
            # or a `Verify:` line in Proposed Fix naming a file that does not exist, each let a
            # bug reach Fixed while the refusal text still said "every acceptance criterion is
            # unticked". Both reproduced through the CLI.
            criteria = sdlc_md.criteria_section(text)
            ticked = bool(_TICKED_RE.search(criteria))
            executable = bool(_VERIFY_RE.search(criteria))
            if type_ == "bug" and not ticked and not executable:
                blocks.append(
                    f"every acceptance criterion is unticked and none carries a `Verify:` "
                    f"line, so nothing speaks for this fix - {target_canon} would be a status "
                    f"the artefact's own body contradicts. Tick what you checked, or add a "
                    f"`Verify:` line that runs. Override with --force")
    # Open Questions, at the VERB and for EVERY type. An artefact must not reach a terminal
    # status still asking a question nobody answered - sixteen did, and every one of them
    # reads as settled work. Both routes out are named in the refusal, because a gate that
    # says only "no" costs a round-trip to discover what yes looks like. One helper, shared
    # with `validate`, so the two cannot disagree about what resolved means.
    if (not force and target_canon
            and sdlc_md.is_terminal_status(type_, target_canon)):
        open_qs = sdlc_md.unresolved_questions(text, root)
        if open_qs:
            listed = "; ".join(open_qs[:4]) + (" ..." if len(open_qs) > 4 else "")
            blocks.append(
                f"{len(open_qs)} unresolved Open Question(s) - {listed}. A terminal artefact "
                f"must not still be asking: either record the ruling by moving the item under "
                f"a `## Resolved Questions` heading, or file the question as a follow-up "
                f"artefact and cite its id on the item. A tick with no destination is refused, "
                f"because that is how a question stops being visible without being answered. "
                f"Override with --force")
    if type_ == "bug" and not force:
        block = _bug_depth_gate(text, target_canon)
        if block:
            blocks.append(f"{block}. Override with --force")
    # US0632: a PLANNED mutant that was never executed, or that SURVIVED, refuses the terminal
    # transition. Every type, not stories: a bug's test plan is a test plan. Opt-in behind a
    # dated cutoff on the same terms as the two-role gate, so an existing backlog carrying no
    # plans is not retro-refused - a gate that refuses everything is a gate that gets switched
    # off wholesale.
    if not force and target_canon in _TERMINAL_FOR_PLAN and _plan_gate_active(root, text):
        # SCOPED TO REPAIRS (US0566). Feature work is already held by a test written before
        # anyone knew which way the implementation would go; only a repair's test is authored
        # with the answer in hand. A blanket demand on all work is the one that gets switched
        # off wholesale, and then it holds nothing.
        repair, why = is_repair_unit(type_, text)
        if repair:
            block = _planned_mutant_gate(root, sdlc_md.norm_id(artifact_id))
            if block:
                blocks.append(f"{block} ({why}). Override with --force")
    # THE MUTATION-EVIDENCE LANE, and it is deliberately NOT nested inside the condition above.
    # The two ask different questions - "was every PLANNED row executed" against "does this
    # repair's changed surface carry evidence" - and they are governed by different settings.
    # Hanging this inside `_plan_gate_active` would make `review.mutation_evidence: block` inert
    # in every project that never set `review.test_plan_after`, while a fixture setting both went
    # green: BG0541's own defect, recreated one level in. Sequential, so the exemption arm also
    # stops silently waiving the planned-mutant gate beside it.
    if not force and target_canon in _TERMINAL_FOR_PLAN:
        lane = mutation_evidence_lane(root, sdlc_md.norm_id(artifact_id), text, type_)
        for block in lane["blocks"]:
            blocks.append(f"{block}. Override with --force")
        if lane["warning"]:
            gate_warn = f"{gate_warn}; {lane['warning']}" if gate_warn else lane["warning"]
    if type_ == "story" and target_canon == "Done":
        parity = _story_target_parity(text)
        if parity:
            # advisory by default (existing projects unaffected); a project opts
            # into refusal via `quality.depth_parity_gate: true`. Read via the
            # gracefully-degrading project_override so a PyYAML-less machine gets the
            # gate decision, not a config-loading crash.
            if sdlc_md.project_override(root, "quality.depth_parity_gate", False) and not force:
                blocks.append(f"{parity}. Override with --force")
            else:
                # ACCUMULATED, as this function's docstring says and as the AC-verify arm below
                # already does. It was a plain assignment, so whichever advisory fired first was
                # silently discarded and which survived depended on statement order.
                # Found while wiring the mutation lane above, whose only reporting path this
                # would have thrown away.
                warn = f"depth-parity advisory: {parity}"
                gate_warn = f"{gate_warn}; {warn}" if gate_warn else warn
    if type_ == "story" and not force and target_canon == "Done":
        # Asked HERE, by the verb that writes the status, rather than only by a lane that runs
        # afterwards. `--force` still overrides and is still recorded, on the same terms as
        # every other forceable close gate - a two-role bypass must be at least as visible.
        two_role = _two_role_gate(root, sdlc_md.norm_id(artifact_id))
        if two_role:
            blocks.append(f"{two_role}. Override with --force")
        block = _done_verify_gate(root, path, text)
        if block:
            # the gate is hard by default; `quality.done_requires_verified: false`
            # downgrades it to advisory-warn (the project sets the policy in .config.yaml).
            # project_override degrades to the default without PyYAML, so the block message
            # is produced rather than a config RuntimeError.
            if sdlc_md.project_override(root, "quality.done_requires_verified", True):
                blocks.append(f"{block}. Override with --force")
            else:
                verify_warn = f"AC-verify advisory (quality.done_requires_verified=false): {block}"
                gate_warn = f"{gate_warn}; {verify_warn}" if gate_warn else verify_warn
    # The tier gate fires on any entry to an implementation status, dry-run included (an
    # honest preflight surfaces the refusal a real run would hit) and force included (the
    # remedy is promotion, not a waiver). Epics are gated too: an epic's planning template
    # asserts its constraint chain, success metrics and risk register "arrive with
    # promotion", and an ungated epic made that assertion false.
    if type_ in tiers.TIERED_TYPES and target_canon in _IMPL_TARGETS:
        block = _tier_gate(root, text, type_)
        if block:
            blocks.append(f"{artifact_id} is not ready for {new_status}: {block}")
    # A request's successful terminal is DERIVED from its children, never asserted (G2): a CR is
    # Complete only when its stories/epics are resolved, an RFC Accepted only when its CRs are.
    # Overridable with --force, like the other close gates. Fires only when the project enforces
    # the two-backlog workflow - an unenforced project completes a CR by assertion, as before.
    if not force and sdlc_md.two_backlog_enforced(root):
        block = _request_terminal_gate(root, type_, artifact_id, target_canon)
        if block:
            blocks.append(f"{block}. Override with --force")
    # The RFC accept gate. Deliberately NOT guarded by `not force`: the sanctioned skip is
    # the recorded override field, so every skip leaves its reason in the artefact. Dry-run
    # included, so a preflight surfaces the refusal a real run would hit.
    if type_ == "rfc":
        block = _rfc_accept_gate(text, target_canon)
        if block:
            blocks.append(f"{artifact_id} -> {new_status}: {block}")
        elif target_canon == "Accepted":
            reason = _rfc_override_reason(text)
            if reason and _rfc_open_decisions(text):
                skip = f"decision-override recorded: {reason}"
                gate_warn = f"{gate_warn}; {skip}" if gate_warn else skip
    # The triage gate fires on any exit from `inbox` for a v3 finding, dry-run included: an
    # honest preflight must surface the same refusal a real run would (never a false green).
    block = _triage_gate(root, type_, text, from_canon, target_canon, triaged_by)
    if block:
        blocks.append(block)
    # Plan-review gate: a story with spec-derived ACs cannot REACH implementation
    # without a recorded independent plan-review verdict. Fires on entry to any state that
    # implies the plan was built - In Progress, Review, or Done - so a direct Ready->Done
    # close cannot smuggle an unreviewed plan into the terminal state. Dry-run included
    # (honest preflight); a no-op on v2 or when the deterministic trigger is not tripped.
    # Not bypassed by --force - the sanctioned skip is the recorded override field, so a
    # skip is always auditable. Idempotent for a forward walk: once reviewed/overridden,
    # In Progress -> Review -> Done all pass.
    if type_ == "story" and target_canon in _IMPL_TARGETS and from_canon not in _IMPL_TARGETS:
        import plan_review  # local import: plan_review pulls route/critic; keep them off cold paths
        pr_res = plan_review.gate(root, artifact_id, path)
        if not pr_res["ok"]:
            blocks.append(pr_res["reason"])
    # TEST-PLAN gate (US0630). A SECOND pre-code gate, beside the spec one above and keyed to a
    # different `Kind`, so neither discharges the other - that separation is BG0510's whole
    # point, and without it one approval clears both while neither reviewer read the other's
    # artefact. Fires on the same entry so a direct Ready->Done cannot smuggle an unreviewed
    # plan into the terminal state, and on EVERY type: a bug's test plan is a test plan.
    if (target_canon in _IMPL_TARGETS and from_canon not in _IMPL_TARGETS
            and _plan_gate_active(root, text)):
        block = _test_plan_gate(root, sdlc_md.norm_id(artifact_id), text)
        if block:
            blocks.append(block)
    if blocks:
        joined = "; AND ".join(blocks)
        raise GateRefusal(f"{artifact_id} -> {new_status} blocked ({len(blocks)} requirement(s), "
                          f"all listed): {joined}.", blocks)
    return gate_warn


def _force_bypassed(root, artifact_id, new_status, type_, path, text,
                    target_canon, from_canon, triaged_by) -> list[str]:
    """What `--force` actually waived on this transition, DERIVED by re-running the same ladder
    with force off - never an enumerated list of "the forceable gates", which would silently
    exempt whichever gate the list forgot.

    Called only after the FORCED ladder has already passed, so any block found here is one force
    is carrying: a gate that ignores force (tier, RFC-accept, plan-review) would have refused the
    forced run too and there would be nothing to record."""
    try:
        _pre_write_gates(root, artifact_id, new_status, type_, path, text,
                         target_canon, from_canon, False, True, triaged_by)
    except GateRefusal as exc:
        return exc.blocks
    except ValueError:
        # Not a gate verdict (an unreadable sibling, a config fault). The transition itself is
        # unaffected, and inventing an override record from an error would be a claim of its own.
        return []
    return []


#: The suffix the ladder appends to a forceable block. Stripped from the RECORD only - the
#: reason is what is being recorded, and "Override with --force" inside a record of an
#: override that already happened reads as an instruction rather than history.
_FORCE_SUFFIX = ". Override with --force"


def _record_force_override(text: str, blocks: list[str], artifact_id: str,
                           new_status: str) -> tuple[str, dict]:
    """Stamp the forced bypass onto the artefact text. Returns (new_text, record).

    Two places, because neither alone is enough. The `Forced-override` field always lands (the
    metadata block is anchored on the Status line this transition just wrote), so the record can
    never be silently dropped; the Revision History row is append-only, so an earlier forced close
    is not overwritten by a later one - but the section is optional, and a record that lands only
    where a section happens to exist is the silent-stand-down class. The returned record says
    which of the two took, so a caller reports what was written rather than what was attempted.
    """
    when = sdlc_md.now_date()
    reasons = "; ".join(b.removesuffix(_FORCE_SUFFIX).strip() for b in blocks)
    summary = f"{when}: --force waived {len(blocks)} gate(s) on {new_status} - {reasons}"
    new_text = _upsert_field(text, "Forced-override", summary)
    new_text, row = append_revision_row(
        new_text, when, "transition set --force",
        f"forced {artifact_id} -> {new_status}, waiving {len(blocks)} gate(s): {reasons}")
    return new_text, {"bypassed": list(blocks), "field": True, "revision_row": row}


def _triage_fields(root, type_, text, from_canon, triaged_by, triage_severity,
                   gate_warn, dry_run) -> tuple[dict, str | None]:
    """The Triaged-by / Triage-severity fields to stamp on a satisfied v3 triage exit, plus the
    (possibly extended) advisory warning. No-op off the (real, non-dry-run) triage path."""
    triage_fields: dict[str, str] = {}
    if not (not dry_run and type_ in sdlc_md.FINDING_TYPES and sdlc_md.is_schema_v3(root)
            and from_canon == sdlc_md.INBOX_STATUS):
        return triage_fields, gate_warn
    # A satisfied triage transition records the triaging seat (and, when given, the
    # triager's severity) at the moment of transition, alongside the raiser's Severity.
    raw_tb = triaged_by or sdlc_md.extract_field(text, "Triaged-by")
    if raw_tb:
        triage_fields["Triaged-by"] = raw_tb
    tb = sdlc_md.parse_authorship_value(raw_tb)
    raiser = sdlc_md.parse_authorship(text, "Raised-by")
    if (tb and raiser and raiser["name"] and tb["type"] == "human"
            and sdlc_md.norm_id(raiser["name"]) == sdlc_md.norm_id(tb["name"])):
        gate_warn = (f"{gate_warn}; solo-human self-triage: {tb['name']}"
                     if gate_warn else f"solo-human self-triage: {tb['name']}")
    if triage_severity:
        triage_fields["Triage-severity"] = triage_severity
    return triage_fields, gate_warn


def _post_write_sync_and_record(root, type_, path, new_text, result, current, new_status,
                                vocab, gate_warn, metrics) -> dict:
    """Write the file, sync the index, cascade the epic (story), and record close telemetry.
    Reports index_synced honestly against residual drift. Behaviour-preserving extraction."""
    sdlc_md.atomic_write(path, new_text)  # truth-file stamp: atomic so a crash never truncates it
    reconcile.apply_type(type_, root)  # sync the index row + counts
    # index_synced is the TRUTH after the sync, not "apply did something": an archived
    # row (apply only edits the live index) or a target status with no summary row both
    # leave residual drift, which we must report honestly rather than claim success.
    norm = sdlc_md.norm_id(result["id"])
    residual = [d for d in reconcile.detect_type(type_, root)["drift"]
                if (d.get("id") and sdlc_md.norm_id(d["id"]) == norm) or d["kind"] == "count-mismatch"]
    result["index_synced"] = not residual
    if residual:
        sync_warn = ("index not fully synced (the artifact may be archived, or its "
                     "new status has no summary row) - run reconcile")
        result["warning"] = f"{gate_warn}; {sync_warn}" if gate_warn else sync_warn
    if type_ == "story":
        result["epic"] = _cascade_epic(root, result["id"],
                                       sdlc_md.canonical_status(new_status, vocab) in _STORY_TICKED)
    from_canon = sdlc_md.canonical_status(current, vocab)
    to_canon = sdlc_md.canonical_status(new_status, vocab)
    if (to_canon in sdlc_md.terminal_statuses(type_)
            and from_canon not in sdlc_md.terminal_statuses(type_)):
        # record on ENTERING the terminal set only: Fixed -> Verified -> Closed is
        # one close (one event), an idempotent re-close is none, and a
        # reopen-then-reclose is honestly a second cycle
        import telemetry  # sibling; record() is best-effort and never raises
        telemetry.record(root, {"id": result["id"], "type": type_, **(metrics or {})})
        result["telemetry"] = True
    return result


RETRACTED = sdlc_md.RETRACTED_DEPTH


def _retract_depth(text: str) -> str:
    """Rewrite a live `Verification depth` into a stated retraction, keeping what it claimed.

    Never INVENTS the field: a unit that claimed no depth has nothing to retract, and writing
    one would manufacture a record of a claim nobody made. Idempotent - retracting a retraction
    would nest the old value inside itself on every subsequent reopen."""
    current = (sdlc_md.extract_field(text, "Verification depth") or "").strip()
    if not current or sdlc_md.depth_retracted(text):
        return text
    return _upsert_field(text, "Verification depth",
                         f"{RETRACTED} on reopen (was: {current}) - re-verify before a "
                         f"terminal status; the previous evidence was withdrawn, not lost")


def _invalidate_verify_report(root: Path, uid: str) -> None:
    """Drop the unit's entry from the verify-report so its overturned green cannot be read
    as current. Best-effort: an absent or unparseable report means there is no stale green to
    withdraw, and a reopen must never fail because a cache could not be written."""
    report = root / _REPORT_REL
    data = sdlc_md.read_json(report, {})
    # A valid-JSON report of the WRONG SHAPE (a list, a string) parses fine and then has no
    # `.get`. Reading it defensively rather than trusting the shape: a reopen must never fail
    # because a cache could not be read, which is what this function's docstring promises.
    stories = data.get("stories") if isinstance(data, dict) else None
    if not isinstance(stories, dict):
        return
    want = sdlc_md.norm_id(uid)
    doomed = [k for k in stories
              if sdlc_md.norm_id(sdlc_md.extract_record_id(str(k)) or "") == want]
    if not doomed:
        return
    for k in doomed:
        stories[k] = {**(stories[k] if isinstance(stories[k], dict) else {}),
                      "verified": 0, "stale": 1,
                      "invalidated_by": "reopen - re-run verify_ac"}
    with contextlib.suppress(OSError):
        sdlc_md.atomic_write(report, json.dumps(data, indent=2) + "\n")


def transition(repo_root: Path | str, artifact_id: str, new_status: str,
               dry_run: bool = False, force: bool = False,
               metrics: dict | None = None, triaged_by: str | None = None,
               triage_severity: str | None = None,
               pending_fields: dict | None = None) -> dict:
    """Set `artifact_id`'s status to `new_status`, sync its index, and cascade the epic
    breakdown for a story. Returns {id, type, from, to, index_synced, epic}.

    A story moving to Done is gated on its AC-verify result: red or never-run
    executable ACs block the transition unless `force=True`. A manual criterion needs a passing
    `**Verified:**` marker, and a criterion carrying NO `Verify:` line is refused the same way -
    the release lane counts it unspecified whatever markers sit beneath it, so exempting it here
    would put the two gates on different answers. Scoped to stories - CR/epic/bug
    closures are unaffected. Manual-only / AC-less stories are never blocked.

    `pending_fields` is a DRY-RUN-ONLY preview of writes the caller performs BEFORE the real
    transition, applied to the in-memory text so the gates judge the state the real run will
    actually see. An orchestrated close annotates `Verification depth` and only then transitions;
    without this the preview evaluated the un-annotated file and refused what the real run
    accepts - the same preview/run divergence in the opposite direction. IGNORED unless
    `dry_run`, so it can never introduce a write of its own.
    """
    root = Path(repo_root)
    if re.match(r"^(RETRO|RV|HO)-?\d+", artifact_id.strip(), re.IGNORECASE):
        raise ValueError(
            f"{artifact_id} is a meta-artifact (retro/review/handoff) outside the status "
            f"machinery by design - edit the file directly; there is no status to cascade")
    path, type_ = _find(root, artifact_id)
    if path is None:
        raise ValueError(f"no artifact found for id {artifact_id!r}")
    vocab = sdlc_md.status_vocab(type_, root)
    if sdlc_md.canonical_status(new_status, vocab) is None:
        raise ValueError(f"{new_status!r} is not a valid {type_} status ({', '.join(vocab)})")
    text = path.read_text(encoding="utf-8")
    if dry_run and pending_fields:
        for _fname, _fval in pending_fields.items():
            text = _upsert_field(text, _fname, _fval)
    target_canon = sdlc_md.canonical_status(new_status, vocab)
    current = sdlc_md.extract_field(text, "Status")
    from_canon = sdlc_md.canonical_status(current, vocab)

    gate_warn = _pre_write_gates(root, artifact_id, new_status, type_, path, text,
                                 target_canon, from_canon, force, dry_run, triaged_by)
    triage_fields, gate_warn = _triage_fields(root, type_, text, from_canon, triaged_by,
                                              triage_severity, gate_warn, dry_run)

    new_text, ok = _set_field(text, "Status", new_status)
    if not ok:
        raise ValueError(f"{path.name} has no `Status` field to transition")
    for fname, fval in triage_fields.items():
        new_text = _upsert_field(new_text, fname, fval)
    reopened = (sdlc_md.is_terminal_status(type_, from_canon or "")
                and not sdlc_md.is_terminal_status(type_, target_canon or ""))
    if reopened:
        new_text = _retract_depth(new_text)
    result = {"id": sdlc_md.extract_record_id(path.stem), "type": type_,
              "from": current, "to": new_status, "index_synced": False, "epic": None,
              "warning": gate_warn}
    if dry_run:
        return result
    if reopened:
        # A reopen is a human overturning a machine verdict. Retracting the depth (above) is
        # only half: `_built_not_closed` and every other reader of "are this unit's ACs green"
        # consult the verify-report, and the vacuous tests that earned the withdrawn green
        # still pass. Invalidating the entry forces a re-run rather than leaving the overturned
        # verdict readable as current.
        _invalidate_verify_report(root, result["id"])
    if force:
        # `--force` advertised the bypass as recorded and recorded nothing, so a forced close of
        # a red-AC story was byte-indistinguishable from a verified one. A force that waived
        # NOTHING is not an override and writes nothing - claiming one would be the same
        # dishonesty pointing the other way.
        bypassed = _force_bypassed(root, artifact_id, new_status, type_, path, text,
                                   target_canon, from_canon, triaged_by)
        if bypassed:
            new_text, result["forced_override"] = _record_force_override(
                new_text, bypassed, result["id"], new_status)
    out = _post_write_sync_and_record(root, type_, path, new_text, result, current,
                                      new_status, vocab, gate_warn, metrics)
    # SURVIVOR FILING, and it happens HERE for one reason: `_pre_write_gates` runs up to three
    # times per `set` - the dry-run preflight, the real transition, and the force-bypass re-run
    # with force off - so a filing inside the gate mints two or three artefacts from one
    # command, and the preflight pass would write during what is contractually a dry run. This
    # is past the `if dry_run: return` above, so a dry run predicts the filing and mints
    # nothing.
    if target_canon in _TERMINAL_FOR_PLAN:
        # NOT gated on `force`. A force taken for an unrelated reason - a red AC, a missing
        # sign-off - would otherwise drop the survivor silently, which is exactly the outcome
        # `report` mode exists to prevent. `--force` waives a BAR; it does not waive a finding.
        filed = _file_surviving_mutants(root, sdlc_md.norm_id(artifact_id), text, type_)
        if filed:
            out["survivors_filed"] = filed
    return out


#: Stamped on a filed survivor bug, and read back as the idempotence key. On the ARTEFACT
#: rather than in a `.local` cache: a cache loss re-mints, and the finding is then in the
#: backlog twice with nothing saying which is which. It also stops the generational hazard -
#: a survivor filed against a survivor bug, for ever - because a unit carrying this field
#: never files another.
SURVIVOR_FIELD = "Mutation-survivor"
#: WHICH RUN let the survivor through. Separate from the key above, which must stay stable
#: across runs so a survivor filed once is never filed again; this one is the scope the close's
#: count needs, and folding it into the key would make every run re-mint the same finding.
SURVIVOR_RUN_FIELD = "Mutation-survivor-run"


def _file_surviving_mutants(root, uid: str, text: str, type_: str) -> list[str]:
    """File each surviving mutant as a severity-rated bug. Returns the ids that now exist.

    The operator's decision: a survivor is a finding to price, not a bar to clear.
    Reporting rather than blocking is only an honest trade if the thing traded away lands
    somewhere a person will see it, so it lands in the backlog rather than in a terminal
    window that closes.
    """
    try:
        import mutation  # noqa: PLC0415
        if mutation.evidence_mode(root) != "report":
            return []
    except (ValueError, ImportError):
        return []
    if sdlc_md.extract_field(text, SURVIVOR_FIELD):
        # A survivor bug never parents another. Without this the first filed finding is itself
        # a repair with no mutation evidence, which files a second, and so on for ever.
        return []
    survivors = _survivor_records(root, uid)
    if not survivors:
        return []
    import file_finding  # noqa: PLC0415
    filed = []
    for mu in survivors:
        existing = _existing_survivor_bug(root, uid, mu)
        if existing:
            filed.append(existing)
            continue
        severity, signal = _survivor_severity(root, mu)
        target, line = mu.get("target"), mu.get("line")
        res = file_finding.file_finding(root, "bug", (
            f"a mutant survives at {target}:{line} - {mu.get('mutant') or 'unnamed'} "
            f"is not pinned by the test {uid} closed on"), {
            "severity": severity,
            "points": 2,
            "affects": f"{target}, {mu.get('test') or '(no test recorded)'}",
            "summary": (
                f"{uid} reached a terminal status carrying a SURVIVING mutant. "
                f"`{mu.get('mutant') or 'the mutant'}` was applied at {target}:{line} and "
                f"{mu.get('test') or 'the recorded test'} stayed green, so nothing pins the "
                f"behaviour that line implements. The finding is about the TEST, not the code: "
                f"an assertion is missing for what the mutant changed.\n\n"
                f"Filed rather than blocked, under `review.mutation_evidence: report`. Fix it, "
                f"or decide to live with it - but decide, rather than not knowing.\n\n"
                f"Severity {severity} was DERIVED: {signal}."),
            "steps": (f"1. Apply `{mu.get('mutant') or 'the mutant'}` at {target}:{line}. "
                      f"2. Run {mu.get('test') or 'the unit test for that behaviour'}. "
                      f"3. It stays green."),
            "fix": (f"Add the assertion the mutant escapes, then re-register: "
                    f"`mutation.py register --unit {uid} --criterion "
                    f"{mu.get('criterion') or 'ACn'} --target {target} --line {line} "
                    f"--mutant '<the edit>' --test '<the command>' --verdict killed`"),
        })
        # The idempotence key is stamped on the ARTEFACT, upserted after the filer wrote it -
        # a `.local` cache re-mints on cache loss, and the finding is then in the backlog twice
        # with nothing saying which is which.
        p = Path(res["path"])
        body = _upsert_field(p.read_text(encoding="utf-8"), SURVIVOR_FIELD,
                             _survivor_key(uid, mu))
        # WHICH RUN let this survivor through, so the close can count the ones IT let through
        # rather than every survivor ever filed. Without it the row's own title - and the
        # criterion, and the changelog - claim a scope the resolver does not have.
        body = _upsert_field(body, SURVIVOR_RUN_FIELD, _open_run_id(root) or "none")
        p.write_text(body, encoding="utf-8")
        filed.append(res["id"])
    return filed


def _open_run_id(root) -> str | None:
    """The open run's id, or None. Best-effort: a filing must never fail on the attribution."""
    try:
        from lib import run_state  # noqa: PLC0415
        return (run_state.read(root) or {}).get("run_id")
    except Exception as exc:  # noqa: BLE001 - attribution must never block a filing
        sdlc_md.debug("transition._open_run_id", exc)
        return None


def _survivor_key(uid: str, mu: dict) -> str:
    """The idempotence key, stamped on the filed artefact.

    HASHED over unit, target, line and mutant. The free-text mutant description used to be in
    the key verbatim, so rewording it inside the filed bug - which a triager does - re-minted
    the same finding. A digest is not a description and nobody edits it into a near-miss.
    """
    import hashlib  # noqa: PLC0415
    raw = f"{uid}@{mu.get('target')}:{mu.get('line')}:{mu.get('mutant') or 'unnamed'}"
    return f"{uid}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _existing_survivor_bug(root, uid: str, mu: dict) -> str | None:
    """The id of a bug already filed for this survivor, or None.

    Read off the ARTEFACTS, so a lost cache cannot re-mint what is already in the backlog.
    """
    key = _survivor_key(uid, mu)
    bugs = Path(root) / "sdlc-studio" / "bugs"
    if not bugs.is_dir():
        return None
    # RECURSIVE. A non-recursive glob missed an archived finding, so archiving a survivor bug
    # re-minted it - which is the one thing a triager does to a finding they have decided about.
    for f in sorted(bugs.rglob("BG*.md")):
        try:
            body = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if (sdlc_md.extract_field(body, SURVIVOR_FIELD) or "").strip() == key:
            return sdlc_md.extract_record_id(f.stem)
    return None


def _survivor_severity(root, mu: dict) -> tuple[str, str]:
    """`(severity, the structural signal it was read from)`, by AST.

    Structural rather than keyword-matched, and it RETURNS ITS REASON, because a severity with
    no stated basis is a verdict triage cannot disagree with:

      * **High** - the enclosing function raises, or returns a value on one path and `None` on
        another. That is this codebase's refusal idiom, so an unpinned line there is an unpinned
        decision about whether to refuse.
      * **Medium** - any other function body: a reporting path.
      * **Low** - module level, or a non-Python target: no decision to get wrong.

    An unparseable file is **Medium, stated as underived**. Never High, which would inflate
    triage on a file nobody could read; never Low, which would bury it. `Critical` is never
    derived - the one machine-decidable critical case is the self-contradicting ledger, and
    that blocks instead of being filed.
    """
    import ast
    target = Path(root) / str(mu.get("target") or "")
    line = mu.get("line")
    if target.suffix != ".py" or not target.is_file() or not line:
        return "Low", f"{mu.get('target')} is not a Python line, so no branch depends on it"
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError) as exc:
        return "Medium", (f"the severity is UNDERIVED - {target.name} could not be parsed "
                          f"({type(exc).__name__}). Medium by default rather than High, which "
                          f"would inflate triage, or Low, which would bury it")
    enclosing = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = getattr(node, "end_lineno", None) or node.lineno
        if node.lineno <= int(line) <= end:
            if enclosing is None or node.lineno > enclosing.lineno:
                enclosing = node                      # innermost wins
    if enclosing is None:
        return "Low", "the line is at module level, so no branch depends on it"
    own = list(_own_scope(enclosing))
    raises = any(isinstance(n, ast.Raise) for n in own)
    returns = [n for n in own if isinstance(n, ast.Return)]
    valued = any(r.value is not None for r in returns)
    if raises:
        return "High", (f"`{enclosing.name}` raises on at least one path, so an unpinned line "
                        f"in it is an unpinned decision about whether to refuse")
    if valued and _has_none_path(enclosing):
        return "High", (f"`{enclosing.name}` returns a value on one path and None on another - "
                        f"this codebase's refusal idiom - so the mutant may have changed which")
    return "Medium", f"`{enclosing.name}` reports rather than refuses, so no gate turns on it"


def _own_scope(fn):
    """Every node in `fn`'s OWN body, excluding nested function and lambda bodies.

    `ast.walk` descends into them, so a pure reporting function containing one nested helper
    that raises derived High with the signal `<the reporter> raises on at least one path` - a
    sentence false of the body it claims to have read. A signal that is wrong is worse than
    none, because the criterion makes it law and triage has no way to check it.
    """
    import ast  # noqa: PLC0415
    nested = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
    stack = list(fn.body)
    while stack:
        node = stack.pop()
        yield node
        # The test is on the NODE, not on its children: guarding the children still descended
        # one level into a nested scope, so a helper's `raise` was read as the enclosing
        # function's. The nested node is yielded (it IS a statement of this body) and its
        # interior is not walked.
        if isinstance(node, nested):
            continue
        stack.extend(ast.iter_child_nodes(node))


def _has_none_path(fn) -> bool:
    """Can `fn` yield None - a bare `return`, or a body that can fall off its end?

    `not isinstance(tail, (Return, Raise))` was the first cut and it was wrong in the other
    direction: an if/else returning a value on BOTH arms ends in an `If`, so it derived a None
    path that does not exist, and the signal said so in words. Terminality is recursive - an
    `If` terminates when both arms do, and a `Try` when its body and every handler do.
    """
    import ast  # noqa: PLC0415
    if any(isinstance(n, ast.Return) and n.value is None for n in _own_scope(fn)):
        return True
    return not _terminates(fn.body)


def _terminates(body) -> bool:
    """Does this statement list always leave by a `return`, a `raise`, or an equivalent?"""
    import ast  # noqa: PLC0415
    if not body:
        return False
    tail = body[-1]
    if isinstance(tail, (ast.Return, ast.Raise)):
        return True
    if isinstance(tail, ast.If):
        return bool(tail.orelse) and _terminates(tail.body) and _terminates(tail.orelse)
    if isinstance(tail, ast.Try):
        handled = all(_terminates(h.body) for h in tail.handlers)
        return _terminates(tail.finalbody) or (_terminates(tail.body) and handled
                                               and (not tail.orelse or _terminates(tail.orelse)))
    if isinstance(tail, (ast.With, ast.AsyncWith)):
        return _terminates(tail.body)
    if isinstance(tail, (ast.For, ast.AsyncFor)):
        # A `for` may run zero times, so only its `else` can be relied on - and the loop body
        # can `break` past the `else`, which is why the body has to terminate too.
        return bool(tail.orelse) and _terminates(tail.body) and _terminates(tail.orelse)
    if getattr(ast, "Match", None) and isinstance(tail, ast.Match):
        # Every case terminates AND one of them is a catch-all, or the match can fall through
        # having matched nothing.
        catch_all = any(isinstance(c.pattern, ast.MatchAs) and c.pattern.pattern is None
                        and c.guard is None for c in tail.cases)
        return catch_all and all(_terminates(c.body) for c in tail.cases)
    if isinstance(tail, ast.While) and isinstance(getattr(tail, "test", None), ast.Constant) \
            and tail.test.value is True:
        return not _breaks_this_loop(tail)
    return False


def _breaks_this_loop(loop) -> bool:
    """Does `loop` contain a `break` that leaves IT, rather than an inner loop?

    `ast.walk` counted an inner loop's break as the outer one's, so a `while True` whose only
    break belongs to a nested `for` was read as escapable and its enclosing function derived a
    None path that does not exist.
    """
    import ast  # noqa: PLC0415
    stack = list(loop.body) + list(getattr(loop, "orelse", []))
    while stack:
        node = stack.pop()
        if isinstance(node, ast.Break):
            return True
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While, ast.FunctionDef,
                             ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue                    # a break in there belongs to that construct
        stack.extend(ast.iter_child_nodes(node))
    return False


def _print_result(res: dict, dry_run: bool) -> None:
    verb = "would set" if dry_run else "set"
    extra = f"; epic {res['epic']} breakdown updated" if res.get("epic") else ""
    print(f"{verb} {res['id']} {res['from']} -> {res['to']}"
          + ("" if dry_run else f" (index synced={res['index_synced']}{extra})"))
    if res.get("warning"):
        print(f"  warning: {res['warning']}")
    ov = res.get("forced_override")
    if ov:
        # A bypass nobody sees is the bypass that gets used. Named on the way past, as well as
        # written to the artefact, so the operator reading the run output knows what force cost.
        where = "artefact field" + (" + revision row" if ov.get("revision_row") else "")
        print(f"  override: --force waived {len(ov['bypassed'])} gate(s), recorded ({where}): "
              + "; ".join(b.removesuffix(_FORCE_SUFFIX).strip() for b in ov["bypassed"]))


def _num(v):
    """int when whole, float otherwise (fractional seconds are a natural unit);
    None only when absent or unparseable - a typo'd metric is dropped visibly by
    the telemetry record simply lacking the field."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f == int(f) else f


def _static_depth_refusal(root, aid: str, depth_value: str, status: str) -> str | None:
    """The depth-gate refusal a one-call close would hit AFTER stamping `depth_value`,
    computed BEFORE any write. Simulates the post-stamp metadata (the flag value wins;
    Production-affecting read from the file, since the Closed gate depends on it) and runs
    the same `_bug_depth_gate` the transition enforces. None when nothing would refuse -
    an unknown id or non-bug type is left to the transition's own reporting."""
    hit = sdlc_md.find_by_id(Path(root), aid)
    if not hit or hit[1] != "bug":
        return None
    vocab = sdlc_md.status_vocab("bug", root)
    canon = sdlc_md.canonical_status(status, vocab)
    prod = sdlc_md.extract_field(hit[0].read_text(encoding="utf-8"), "Production-affecting") or ""
    sim = f"> **Verification depth:** {depth_value}\n"
    if prod:
        sim += f"> **Production-affecting:** {prod}\n"
    return _bug_depth_gate(sim, canon)


def cmd_set(args: argparse.Namespace) -> int:
    # Natural positional form `set <ID> <STATUS>` maps onto --id/--status, so the obvious first
    # attempt works. The flags still work; giving the SAME value both ways is refused rather than
    # silently picking one.
    idpos, statuspos = getattr(args, "idpos", None), getattr(args, "statuspos", None)
    if idpos:
        if args.id or getattr(args, "ids", None):
            print("error: give the id EITHER positionally (`set <ID> <STATUS>`) OR via "
                  "--id/--ids, not both", file=sys.stderr)
            return 2
        args.id = [idpos]
    if statuspos:
        if args.status:
            print("error: give the status EITHER positionally (`set <ID> <STATUS>`) OR via "
                  "--status, not both", file=sys.stderr)
            return 2
        args.status = statuspos
    ids = sdlc_md.resolve_ids(args)
    if not ids:
        print("specify at least one id: `set <ID> <STATUS>` (positional), or --id (repeatable) / "
              "--ids as a comma list", file=sys.stderr)
        return 2
    if not args.status:
        print("specify the target status: `set <ID> <STATUS>` (positional), or --status",
              file=sys.stderr)
        return 2
    # One-call close (the three-verb ceremony was easy to half-do): --depth stamps
    # `Verification depth`, --reviewer/--author record the independent verdict, then the
    # gated transition runs - with every PREDICTABLE refusal raised before any write.
    reviewer, author = getattr(args, "reviewer", None), getattr(args, "author", None)
    if reviewer or author:
        if not (reviewer and author and args.verdict):
            print("error: the one-call verdict needs --verdict, --reviewer AND --author "
                  "together (or none, to skip recording one). To stamp an identity alone "
                  "(e.g. an acceptance author) with no verdict, use `transition annotate`.",
                  file=sys.stderr)
            return 2
        import critic
        independent, why = critic.independence(reviewer, author)
        if not independent:
            print(f"error: {why} - independence is the floor, so nothing was written",
                  file=sys.stderr)
            return 2
    # Parse the per-attempt list ONCE, up front: a malformed --attempt is a usage error, not a
    # per-id block, so it must fail fast (rc 2) before any id is touched, not be caught and
    # re-reported once per id inside the loop.
    import telemetry
    try:
        attempts = telemetry.parse_attempts(getattr(args, "attempt", None),
                                            getattr(args, "attempts", None))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    results = []
    refused = 0
    # The pre-writes this close performs BEFORE the gated transition, as the dry-run preview
    # they must be judged against. `pending_fields` is ignored unless dry_run, so passing it
    # on the real call is inert - and passing it on the user-facing --dry-run is what stops the
    # preview judging an un-stamped file and refusing what the identical real command accepts.
    pending = {"Verification depth": args.depth} if getattr(args, "depth", None) else None
    pre_writes = bool(pending) or bool(reviewer)
    for aid in ids:
        try:
            if getattr(args, "depth", None):
                # Pre-flight the depth gate against the WOULD-BE stamped text: an
                # undershoot (e.g. --depth smoke --status Verified) is a pure function
                # of the flags, so it must refuse BEFORE the stamp or verdict land -
                # the same gate the transition runs, just simulated pre-write.
                reason = _static_depth_refusal(args.root, aid, args.depth, args.status)
                if reason:
                    raise ValueError(f"pre-write: {reason}")
            if pre_writes and not args.dry_run:
                # The depth gate is not the only predictable refusal, and the others ran AFTER
                # the stamp and the verdict row - so a refused close left a depth stamp and a
                # persistent APPROVE for a close that never happened. Run the WHOLE ladder as a
                # dry-run first, against the text the real run will see; a refusal raises here,
                # before anything is written.
                transition(args.root, aid, args.status, dry_run=True, force=args.force,
                           triaged_by=args.triaged_by, triage_severity=args.triage_severity,
                           pending_fields=pending)
            if getattr(args, "depth", None) and not args.dry_run:
                annotate(args.root, aid, "Verification depth", args.depth)
            if reviewer and not args.dry_run:
                import critic
                critic.record_verdict(args.root, aid, args.verdict, reviewer, author)
            metrics = {k: v for k, v in {"iterations": _num(args.iterations),
                                         "wall_time_s": _num(args.wall_time_s),
                                         "tokens": _num(getattr(args, "tokens", None)),
                                         "model": getattr(args, "model", None),
                                         "attempts": attempts,
                                         "critic_verdict": args.verdict}.items() if v is not None}
            res = transition(args.root, aid, args.status, dry_run=args.dry_run,
                             force=args.force, metrics=metrics,
                             triaged_by=args.triaged_by, triage_severity=args.triage_severity,
                             pending_fields=pending)
            results.append(res)
            if args.format != "json":
                _print_result(res, args.dry_run)
        except (ValueError, FileNotFoundError) as exc:
            # one refusal never aborts the rest - each id is individually gated
            refused += 1
            results.append({"id": aid, "blocked": str(exc)})
            if args.format != "json":
                print(f"  blocked  {aid}: {exc}")
    if args.format == "json":
        print(json.dumps(results if len(ids) > 1 else results[0], indent=2))
    if len(ids) > 1:
        out = sys.stderr if args.format == "json" else sys.stdout
        print(f"batch: {len(ids) - refused}/{len(ids)} transitioned, {refused} blocked", file=out)
    return 1 if refused else 0


def cmd_annotate(args: argparse.Namespace) -> int:
    try:
        r = annotate(args.root, args.id, args.field, args.value)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"annotated {args.id}: {args.field} = {args.value}"
               + ("" if r["changed"] else " (already set)"))
    return 0


#: A ticked acceptance criterion (`- [x]`) and an executable one (a `Verify:` line). EITHER
#: satisfies the terminal gate: the first is a human saying they checked it, the second is the
#: machine saying so. Requiring both would refuse the ordinary judgement call a bug fix is.
_TICKED_RE = re.compile(r"^\s*[-*]\s*\[[xX]\]", re.M)
_VERIFY_RE = re.compile(r"^\s*[-*]\s*\*\*Verify:\*\*", re.M)


#: Terminal statuses a test plan has to have been executed for.
_TERMINAL_FOR_PLAN = ("Done", "Fixed")


def _plan_gate_active(root, text: str) -> bool:
    """Is the planned-mutant gate in force for this unit?

    Dated cutoff, exactly like the two-role rule: `review.test_plan_after` names the creation
    date on or after which units are held. Absent, the gate stands down entirely - an existing
    backlog carrying no plans must not be retro-refused, because a gate that refuses every unit
    in a backlog is one that gets switched off wholesale rather than satisfied.
    """
    # AN UNREADABLE CONFIG IS NOT AN ABSENT CUTOFF. `project_override` swallows every config
    # fault and returns the default, so `not after` read a malformed, non-UTF-8, unreadable or
    # directory-shaped `.config.yaml` as "this project set no cutoff" and switched BOTH new gates
    # off entirely. A seat reproduced it four ways. The sibling `_two_role_gate` already solved
    # this exact case with the helper below, and its comment enumerates the same four shapes -
    # the repair reached parity with that gate's LEDGER half and skipped its CONFIG half.
    cfg = Path(root) / "sdlc-studio" / ".config.yaml"
    if cfg.exists() and sdlc_md.config_unparseable(cfg):
        return True          # in scope, and `_test_plan_gate` will report why it cannot judge
    after = sdlc_md.project_override(root, "review.test_plan_after", None)
    if not after:
        return False
    created = (sdlc_md.extract_field(text, "Created") or "").strip()
    return bool(created) and created >= str(after).strip()


def _planned_mutant_gate(root, unit: str) -> str | None:
    """Refuse a terminal transition while a planned mutant is unexecuted or alive.

    The finding is about the TEST, so the message points at the criterion rather than at the
    mutant: a survivor means the test that criterion names did not notice a change to the code
    it claims to pin. `not-run` is refused on the same terms - a plan whose rows are optional
    measures nothing, and an unexecuted plan must not read like a passed one.
    """
    try:
        import mutation  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        res = mutation.plan_execution(root, unit)
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        # Same rule as `_test_plan_gate` above. Latent here only because `_load_ledger` happens
        # to catch OSError one layer down - a defence that depends on somebody else's accident
        # is not a defence.
        return (f"the planned-mutant gate could not be established ({type(exc).__name__}: "
                f"{exc}) - an unreadable bar is not a passed one")
    if res.get("errors"):
        return (f"{unit} has no `## Test Plan`, and `review.test_plan_after` puts it in scope - "
                f"derive one with `verify_ac.py testplan derive --unit {unit}`")
    outstanding = res.get("outstanding") or []
    if not outstanding:
        return None
    parts = []
    for r in outstanding:
        if r["verdict"] == mutation.NOT_RUN:
            parts.append(f"{r['ac']} was planned and never executed")
        else:
            parts.append(f"{r['ac']}'s mutant SURVIVED on {r.get('target')} - the test that "
                         f"criterion names did not notice `{r['mutant'][:60]}`")
    return (f"{unit}: {len(outstanding)} planned mutant(s) unaccounted for - " + "; ".join(parts)
            + f". Check them with `mutation.py run --story {unit} --from-plan`")


#: The provenance fields that mark a unit as REPAIR work. Read from the artefact's own metadata,
#: never inferred from prose: "fix", "repair" and "regression" appear in the titles of plenty of
#: feature stories, and a classifier reading words would type them wrongly in the direction that
#: costs most - holding new capability to a bar the evidence indicts only repairs for.
_REPAIR_PARENT_PREFIXES = ("BG", "RV")


def is_repair_unit(type_: str, text: str) -> tuple[bool, str]:
    """Is this unit REPAIR work, and which field says so?

    `(bool, why)` - the reason is returned so a refusal can name the field it read rather than
    asserting a classification the reader cannot check.

    The scope matters as much as the rule. A blanket mutation demand on ALL work is the one that
    gets switched off wholesale: feature work is already held by a test written before anyone
    knew which way the implementation would go, and only a repair's test is authored with the
    answer already in hand. Widening the demand past that dilutes it to nothing.
    """
    if type_ == "bug":
        return True, "its type is `bug`"
    parent = (sdlc_md.extract_field(text, "Parent") or "").strip()
    delivers = (sdlc_md.extract_field(text, "Delivers") or "").strip()
    for field, value in (("Parent", parent), ("Delivers", delivers)):
        ident = sdlc_md.norm_id(value.split(",")[0].strip()) if value else ""
        if ident[:2] in _REPAIR_PARENT_PREFIXES:
            return True, f"its `{field}` names {ident}, a finding rather than a request"
    return False, "no type or provenance field marks it as repair work"


def no_surface_record(root, unit: str) -> dict | None:
    """The recorded no-mutatable-surface exemption for `unit`, or None."""
    import json  # noqa: PLC0415
    path = Path(root) / "sdlc-studio" / ".local" / "no-mutatable-surface.json"
    try:
        return (json.loads(path.read_text(encoding="utf-8")) or {}).get(sdlc_md.norm_id(unit))
    except (OSError, ValueError):
        return None


def verify_no_surface_claim(root, unit: str, record: dict, text: str = "") -> str | None:
    """Re-derive the claim rather than trusting it. Returns a refusal, or None when it holds.

    An exemption nobody checks is a box, and this one exempts a unit from the only evidence its
    author could not have manufactured.

    THE SCOPE IS THE DIFF, and ONLY the diff. Re-deriving over the author's own declaration
    checks that the author was consistent with themselves, which is not a check at all: a
    hand-written record naming `README.md` exempted a repair whose `Affects` was a mutatable
    module, because the generator dutifully found nothing in the markdown file it was handed.

    `Affects` is deliberately NOT intersected in, though the first draft did exactly that. A
    declaration can only ever SHRINK the derived surface, so intersecting it hands the author
    back the same fail-open one step over: mis-declare `Affects`, and the module you changed
    stops being looked at. The diff is the one source the author does not get to write, so it
    is the whole source. `Affects` appears in the refusal as context and decides nothing.

    The cost is over-refusal in a multi-unit run, where the diff carries a sibling's work too.
    That is the safe direction: an exemption wrongly refused is answered by recording an
    accurate one, and an exemption wrongly granted is answered by nobody, because nothing
    downstream can tell it happened.

    An EMPTY base ref refuses rather than granting. The fallback fails the worse way here: a
    derivation that cannot run returns an empty set, an empty set produces no mutant, and no
    mutant reads as the claim holding - so every exemption would be granted by the one condition
    under which nothing was checked. That is the fail-open this function exists to close, one
    layer down from where it was found.
    """
    try:
        import mutation  # noqa: PLC0415
        from lib import run_state  # noqa: PLC0415
        base = (run_state.base_ref(root) or "").strip()
        why = None
        if not base:
            why = "no run is open, so there is no base ref to diff against"
        elif subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
                            cwd=str(root), capture_output=True).returncode != 0:
            # NOT the same condition as an absent ref, and it was the wider hole. `changed_lines`
            # swallows a failed `git diff` and returns an empty map, so an unresolvable base -
            # a SHA lost to an amend, a stale clone, a branch that has gone - produced no mutant,
            # and no mutant read as the claim holding. That is AC7's own defect one condition
            # over, and it is reachable without anybody trying.
            why = (f"the recorded base ref {base[:12]} does not resolve to a commit in this "
                   f"tree, so the diff it would be derived from cannot be taken")
        if why:
            return (f"{unit}: the no-mutatable-surface claim cannot be re-derived because "
                    f"{why}. An exemption is refused rather than granted here: a derivation "
                    f"that cannot run produces no mutant, and no mutant is indistinguishable "
                    f"from a claim that holds")
        changed = mutation.changed_lines(root, base)
        surface = [p for p in (Path(f) for f in changed)
                   if p.is_file() and p.suffix == ".py"]
        muts, _unchecked = (mutation.mutants_over_changed_lines(root, surface, base)
                            if surface else ([], {}))
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        return (f"{unit}: the no-mutatable-surface claim could not be re-derived "
                f"({type(exc).__name__}: {exc}) - an unverifiable exemption is not a granted one")
    if muts:
        first = muts[0]
        claimed = ", ".join(p for p in (record or {}).get("paths", []) if p) or "nothing"
        declared = ", ".join(sdlc_md.affects_files(text or "")) or "nothing"
        return (f"{unit}: the no-mutatable-surface record claims nothing could be mutated over "
                f"{claimed} (its `Affects` declares {declared}), and the generator produces "
                f"{len(muts)} mutant(s) over the changed "
                f"lines the DIFF gives - starting at {first['file']}:{first['line']} "
                f"({first['class']}). The scope is the diff against {base[:12]}, not the paths "
                f"the record names: an exemption re-derived from its own declaration checks "
                f"only that its author was consistent with themselves")
    return None


def mutation_evidence_lane(root, unit: str, text: str, type_: str) -> dict:
    """What this repair's mutation evidence says, and what the project's mode DOES about it.

    A PURE READ. It writes nothing, mints nothing and has no side effect, so the gate ladder can
    call it as many times as it likes - and `_pre_write_gates` runs up to three times per `set`.
    Anything that must happen ONCE per command happens in `transition()`, on the far side of the
    dry-run return, never here.

    Returns `{mode, blocks, warning, survivors, exempt}`. The caller decides; this decides
    nothing except what is true.

    The mode table, and why two rows ignore it:

    | state                              | report      | block | off   |
    | ---------------------------------- | ----------- | ----- | ----- |
    | no record / STALE / vacuous zero   | warning     | block | quiet |
    | survivor                           | FILED + through | block | quiet |
    | a FALSE exemption                  | **block**   | block | quiet |
    | recorded `killed`, measured `survived` | **block** | block | **block** |

    A false exemption blocks under `report` because it is not a quality bar: it is a claim
    re-derived and found untrue. `report` trades a hard bar for a filed finding; it does not
    trade away the truth of a statement the author made in writing.

    A ledger that contradicts ITSELF blocks in every mode including `off`, because that is
    instrument integrity rather than a bar. `off` says "do not hold my transitions on mutation
    evidence"; it cannot say "let the instrument lie", because every figure derived from a false
    verdict is wrong and nothing downstream can tell.
    """
    import mutation  # noqa: PLC0415
    out: dict = {"mode": None, "blocks": [], "warning": None, "survivors": [], "exempt": False}
    repair, why = is_repair_unit(type_, text)
    if not repair:
        return out
    uid = sdlc_md.norm_id(unit)
    try:
        out["mode"] = mode = mutation.evidence_mode(root)
    except ValueError as exc:
        # Refused BY NAME, in every mode, because the mode is the thing that could not be read.
        out["blocks"].append(str(exc))
        return out

    # The contradiction check runs FIRST and ignores the mode entirely - see the docstring.
    contradiction = _ledger_contradiction(root, uid)
    if contradiction:
        out["blocks"].append(contradiction)
    if mode == "off":
        # STOOD DOWN, as the doctrine says, rather than run and discarded. Everything below
        # shells out to git and runs the mutant generator; doing that work only to throw the
        # answer away is not what "the lane stands down" means to somebody reading it, and it
        # is a real cost on a project that chose `off` to avoid paying it.
        return out

    record = no_surface_record(root, uid)
    if record:
        out["exempt"] = True
        refusal = verify_no_surface_claim(root, uid, record, text)
        if refusal and mode != "off":
            out["blocks"].append(refusal)
        return out

    reason = repair_mutation_gate(root, uid, text)
    if not reason:
        return out
    out["survivors"] = _survivor_records(root, uid)
    if mode == "block":
        out["blocks"].append(f"{reason} ({why})")
    elif mode == "report":
        out["warning"] = f"mutation-evidence advisory ({why}): {reason}"
    return out


def _survivor_records(root, uid: str) -> list[dict]:
    """The surviving mutants recorded for `uid`, as records rather than as a sentence.

    Returned as data because the filer needs the target, the line, the criterion and the test
    to compose a finding somebody can act on, and re-parsing them back out of the refusal's
    prose is guesswork about a format nothing pinned.
    """
    try:
        import mutation  # noqa: PLC0415
        entries = mutation.ledger_entries(root)
    except Exception:  # noqa: BLE001 - a lane that cannot read the ledger reports no survivor
        return []
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        for mu in (e.get("mutants") or []):
            if (isinstance(mu, dict) and mu.get("unit") == uid
                    and mu.get("verdict") == "survived"):
                out.append({"target": e.get("target"), "line": mu.get("line"),
                            "mutant": mu.get("mutant"), "test": mu.get("test"),
                            "criterion": mu.get("criterion"), "unit": uid})
    return out


def _mutant_identity(mu: dict) -> str:
    """What was applied, normalised enough to join a measured row to a registered one.

    A measured row names its FAULT CLASS (`stub-return-null`); a registered one names the edit
    in the author's own words. Neither is the other, so the join is on the normalised text and a
    registered mutant that names its class joins the measured row for that class. Anything else
    is a different mutant, which is the point: two different mutants at one line are two honest
    statements, not the instrument contradicting itself.
    """
    return " ".join(str(mu.get("mutant") or "").lower().split())


def _ledger_contradiction(root, uid: str) -> str | None:
    """A mutant recorded `killed` and MEASURED `survived` at the same target, line and hash.

    Not a quality bar - the instrument reporting two different things about one fact. It refuses
    under `off` as well, which no other row here does, because `off` is a decision about whether
    mutation evidence holds a transition, not permission for the ledger to be false.
    """
    try:
        import mutation  # noqa: PLC0415
        entries = mutation.ledger_entries(root)
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        # An unreadable bar is not a passed one, which is what both sibling gates say in the
        # same position. Returning None here made the one check that refuses in EVERY mode -
        # `off` included - silently pass exactly when the ledger could not be read.
        return (f"{uid}: the mutation ledger could not be read to check it against itself "
                f"({type(exc).__name__}: {exc}) - an instrument nobody can read is not one "
                f"that has been shown honest")
    seen: dict = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        key_base = (e.get("target"), e.get("hash"))
        for mu in (e.get("mutants") or []):
            if not isinstance(mu, dict) or mu.get("unit") != uid:
                continue
            verdict, line = mu.get("verdict"), mu.get("line")
            if verdict not in ("killed", "survived") or line is None:
                continue
            # THE MUTANT is part of the key, not just the line. Two different mutants at one
            # line are two honest statements, and reading them as a contradiction turned the
            # default `report` mode into a block no config could stand down - this branch
            # ignores the mode by design, so a false positive here is not survivable. The
            # instrument lying about ITSELF means one mutant, two verdicts.
            key = (*key_base, line, _mutant_identity(mu), mutation.entry_provenance(e))
            prior = seen.get(key)
            if prior and prior[0] != verdict:
                return (f"{uid}: the mutation ledger CONTRADICTS itself at "
                        f"{e.get('target')}:{line} - recorded {prior[0]!r} by "
                        f"{prior[1]} and {verdict!r} by "
                        f"{mutation.entry_provenance(e)}, under the same content hash. This "
                        f"refuses in every mode, `off` included: the instrument is reporting "
                        f"two different things about one fact, and every figure derived from "
                        f"the false one is wrong with nothing downstream able to tell")
            seen[key] = (verdict, mutation.entry_provenance(e))
    return None


def repair_mutation_gate(root, unit: str, text: str, base_ref: str | None = None) -> str | None:
    """Mutation evidence over a repair's OWN CHANGED LINES, re-read from the record.

    Three states, kept apart because they have different fixes and only one of them is the
    author's omission:
      * no record at all - the evidence was never gathered;
      * a record whose target content has MOVED since - the run was real but is about bytes the
        file no longer has, so it is STALE rather than green. Without this a passing run can be
        banked and spent against later edits, which is a gate you satisfy once;
      * a record covering the current bytes - the gate opens.

    The caller never gets to assert a pass. A gate that accepts the claim it exists to check is
    a box, and this one guards the only evidence a fix's author could not have manufactured.
    """
    import hashlib  # noqa: PLC0415
    try:
        import mutation  # noqa: PLC0415
        affects = [Path(root) / a for a in sdlc_md.affects_files(text)]
        targets = [a for a in affects if a.is_file() and a.suffix == ".py"]
        if not targets:
            return None                      # no mutatable surface - US0566's exemption path
        entries = mutation.ledger_entries(root)
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        return (f"the repair-mutation gate could not be established ({type(exc).__name__}: "
                f"{exc}) - an unreadable bar is not a passed one")

    uid = sdlc_md.norm_id(unit)
    mine = [e for e in entries if isinstance(e, dict)
            and any(isinstance(m, dict) and m.get("unit") == uid
                    for m in (e.get("mutants") or []))]
    if not mine:
        return (f"{uid} is repair work and carries NO mutation evidence over its changed lines. "
                f"Apply a mutant to what it changed, watch its test fail, and record it: "
                f"`mutation.py register --unit {uid} --criterion ACn --target <file> "
                f"--line <n> --mutant <the edit> --test <the command> --verdict killed`")

    stale = []
    for e in mine:
        target = Path(root) / str(e.get("target") or "")
        if not target.is_file():
            continue
        now = hashlib.sha256(target.read_bytes()).hexdigest()
        if e.get("hash") and e["hash"] != now:
            stale.append(str(e.get("target")))
    # SURVIVORS, and the vacuous zero. `survivors == 0` over an EMPTY mutant set is not a pass -
    # it is the same shape as `ac=0 pass=0` reading as a clean pass, one instrument
    # over. A run is judged on what it applied, never on its own exit status: a run that
    # completes is evidence a run happened and says nothing about what it found.
    applied = survivors = 0
    living: list = []
    for e in mine:
        for mu in (e.get("mutants") or []):
            if not isinstance(mu, dict) or mu.get("unit") != uid:
                continue
            if mu.get("verdict") == mutation.EQUIVALENT_VERDICT:
                continue          # excluded by design, and visibly so
            applied += 1
            if mu.get("verdict") == "survived":
                survivors += 1
                living.append(f"{e.get('target')}:{mu.get('line') or '?'} "
                              f"({mu.get('mutant') or 'unnamed mutant'})")
    if applied == 0:
        return (f"{uid}: the recorded mutation run applied NO mutant, so a survivor count of "
                f"zero says nothing. `survivors == 0` over an empty set is vacuous - the same "
                f"shape as a clean pass over criteria nobody read")
    if survivors:
        listed = "; ".join(living[:5])
        return (f"{uid}: {survivors} of {applied} mutant(s) SURVIVED - {listed}. The finding is "
                f"about the TEST: an assertion is missing for the behaviour each names. The "
                f"verdict is the SURVIVOR count, never the run's own exit status - a run that "
                f"completes is evidence a run happened")

    if stale and len(stale) == len(mine):
        return (f"{uid}'s mutation evidence is STALE, not absent: every recorded run covers "
                f"bytes {', '.join(sorted(stale))} no longer has. A run banked against an "
                f"earlier surface cannot be spent on this one - re-run it over the current "
                f"changed lines")
    return None


def _test_plan_gate(root, unit: str, text: str) -> str | None:
    """Refuse entry to implementation while the unit's test plan is missing or unreviewed.

    The two refusals are DISTINCT, and that is the criterion rather than a nicety: "no plan" and
    "plan not reviewed" have different fixes, and one message for both sends the reader to the
    wrong command. Reviewing the test costs a fraction of reviewing the code, so being sent to
    the wrong one of those two is not a small error.

    The review is looked up under the `test-plan` KIND. A spec-review approval must not discharge
    this gate: its reviewer never saw a test plan, and BG0510 exists because the ledger's shape
    made exactly that substitution the default.
    """
    if "## Test Plan" not in text:
        return (f"{unit} has no `## Test Plan`, and `review.test_plan_after` puts it in scope - "
                f"name, per criterion, the production change its test must fail on. Derive it: "
                f"`verify_ac.py testplan derive --unit {unit}`")
    try:
        import critic  # noqa: PLC0415 - deferred sibling, as elsewhere in this module
        v = critic.verdict_for(root, unit, phase="plan-review", kind="test-plan")
    except Exception as exc:  # noqa: BLE001 - report it, never swallow it
        # Fail LOUD, on the same terms as the two sibling gates in this file. `return None` is
        # PASS, so the one condition under which this gate was least able to judge - an
        # unreadable ledger, broken tooling - was the one under which it approved everything.
        # An independent seat chmod-ed the verdict ledger and watched a refusal become exit 0
        # with nothing on either stream. An unreadable bar is not a passed one.
        return (f"the test-plan gate could not be established ({type(exc).__name__}: {exc}) - "
                f"an unreadable bar is not a passed one")
    if v and v.get("verdict") == critic.APPROVE and critic.is_independent(v):
        return None
    why = ("no plan-review verdict of kind `test-plan` is on record"
           if not v else
           f"the plan-review verdict on record is {v.get('verdict')} by "
           f"{v.get('reviewer') or '-'} against author {v.get('author') or '-'}"
           + (" - a self-review never clears the gate" if not critic.is_independent(v) else ""))
    return (f"{unit} has a test plan that no independent seat has approved - {why}. Reviewing "
            f"the test costs a fraction of reviewing the code, which is the whole reason this "
            f"gate is here. Brief one: `critic.py brief --unit {unit} --seat qa "
            f"--phase plan-review`, then record it with `critic.py record --unit {unit} "
            f"--phase plan-review --kind test-plan --verdict APPROVE --brief <fingerprint>`")


def requirements(root, artifact_id: str, target: str) -> list[str]:
    """The unmet requirements standing between `artifact_id` and `target`. Writes nothing.

    Asked BEFORE the work, so the requirement is met as part of it rather than discovered as
    a refusal afterwards. Five `Verification depth` refusals in one session, each after the
    unit was otherwise finished, is what this exists to stop.

    Derived, never restated. This RUNS the real gate ladder via the dry-run path and reports
    what it refuses, so there is no second copy of a requirement to drift from the guard that
    enforces it. A hand-maintained list here would be a duplicate that goes stale silently -
    the failure mode this command is supposed to remove, reintroduced one layer up.
    """
    try:
        transition(root, artifact_id, target, dry_run=True)
    except GateRefusal as exc:
        # The blocks come from the ladder as a LIST. An earlier version rebuilt them by
        # splitting the message on `". Override with --force"`, which only some gates append -
        # so two adjacent gates without it merged into one item, and an alternating pair leaked
        # the `"; AND "` delimiter into the next. The count then disagreed with the count the
        # gate itself had just reported.
        # removesuffix, not rstrip: rstrip strips EVERY trailing dot, so a future reason
        # ending "e.g." or "..." would be silently trimmed. A no-op on today's gates (none
        # ends in a period) - latent, and cheap to close now rather than to debug later.
        return [b.strip().removesuffix(".") for b in exc.blocks if b.strip()]
    # Any OTHER error - an unknown id, a status outside the vocabulary - is an error, not a
    # requirement. Reporting it as "something you must satisfy" would be the confidently wrong
    # answer this command exists to end, so it propagates.
    return []


def cmd_requirements(args) -> int:
    unmet = requirements(args.root, args.id, args.status)
    if args.format == "json":
        print(json.dumps({"id": args.id, "target": args.status, "unmet": unmet}, indent=2))
        return 0
    if not unmet:
        print(f"{args.id} -> {args.status}: no unmet requirements")
        return 0
    print(f"{args.id} -> {args.status}: {len(unmet)} unmet requirement(s)")
    for item in unmet:
        print(f"  - {item}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transition an artifact's status + cascade.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set", help="Set an artifact's status and sync index + epic breakdown.")
    # The natural form `set <ID> <STATUS>` is accepted as well as the --id/--status flags, so the
    # obvious first attempt works instead of erroring on argparse noise (they map onto the flags in
    # cmd_set; mixing the two forms for the same value is refused there).
    s.add_argument("idpos", nargs="?", metavar="ID",
                   help="artifact id, positional - the natural form `set <ID> <STATUS>`")
    s.add_argument("statuspos", nargs="?", metavar="STATUS",
                   help="new status, positional - the natural form `set <ID> <STATUS>`")
    sdlc_md.add_ids_argument(s, help_="artifact id, e.g. CR0042 / US0023; repeat --id or pass "
                                      "--ids as a comma list for a same-target batch (each id is "
                                      "individually gated, one refusal never aborts the rest)")
    s.add_argument("--status", help="New status (must be in the type vocabulary); or give it "
                                    "positionally as `set <ID> <STATUS>`")
    s.add_argument("--root", default=".")
    s.add_argument("--iterations", help="run metric passed to the terminal-close telemetry event")
    s.add_argument("--wall-time-s", dest="wall_time_s", help="run metric for the telemetry event")
    s.add_argument("--tokens", help="run metric: total tokens the unit cost, on the telemetry event")
    s.add_argument("--model", help="run metric: the model that delivered the unit (stamped on the "
                                   "artefact and the telemetry event)")
    s.add_argument("--attempt", action="append", metavar="MODEL:TOKENS",
                   help="one model invocation on this unit, e.g. haiku:1000. Repeatable and "
                        "order-preserving - a close that ESCALATED (cheap model rejected, "
                        "re-run on a dearer one) records every attempt, so the true cost is "
                        "their sum, not the final line. Threaded to the telemetry close event")
    s.add_argument("--attempts", metavar="JSON",
                   help="the per-attempt list as a JSON array of {model, tokens} - the structured "
                        "form of --attempt for a caller that already holds the list")
    s.add_argument("--verdict", help="critic verdict recorded on the telemetry event (and, with "
                                     "--reviewer/--author, in the critic log)")
    s.add_argument("--depth", help="one-call close: stamp `Verification depth` with this value "
                                   "before the gated transition (replaces a separate annotate)")
    s.add_argument("--reviewer", help="one-call close: record the critic verdict under this "
                                      "reviewer (must differ from --author)")
    s.add_argument("--author", help="one-call close: the authoring seat the reviewer judged "
                                    "(reviewer != author enforced before any write)")
    s.add_argument("--force", action="store_true",
                   help="bypass the forceable close gates (story->Done AC-verify, bug depth, "
                        "request-terminal). Every gate it actually waives is named in a "
                        "`Forced-override` field on the artefact and in its Revision History; "
                        "gates whose sanctioned skip is a recorded reason (RFC decisions, "
                        "plan review) and the tier gate are NOT bypassed")
    s.add_argument("--triaged-by", dest="triaged_by",
                   help="v3 triage: the triaging seat as `Name; type; version` (type is "
                        "human|persona|agent); required and recorded on an inbox->triaged "
                        "transition, must differ from the raiser (separation of duties)")
    s.add_argument("--triage-severity", dest="triage_severity",
                   help="v3 triage: the triager's severity, recorded alongside the raiser's")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_set)
    r = sub.add_parser("requirements",
                       help="What a transition will require, asked BEFORE the work. Writes "
                            "nothing; derived by running the real gates, never a restatement.")
    r.add_argument("--id", required=True, help="Artifact id, e.g. BG0042 / US0023")
    r.add_argument("--status", required=True, help="The target status you intend to reach")
    r.add_argument("--root", default=".")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_requirements)
    a = sub.add_parser("annotate", help="Set/update one metadata field on an artifact "
                                        "(deterministic stamp; index untouched).")
    a.add_argument("--id", required=True, help="Artifact id, e.g. BG0042 / US0023")
    a.add_argument("--field", required=True, help="Field name, e.g. 'Verification depth'")
    a.add_argument("--value", required=True)
    a.add_argument("--root", default=".")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_annotate)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the same
    # tree. Resolving it at only one call site let the two disagree - the resolved value
    # guarded the run while each verb still wrote through a bare `--root .`, so a run
    # from a subdirectory acted on a stray workspace beside the cwd and exited 0.
    args.root = str(sdlc_md.resolve_root(args))
    # A status change recorded through a mutated tool is a record nobody can trust
    # afterwards, so the applied-mutant window is a refusal, not a warning.
    refusal = sdlc_md.inflight_refusal(sdlc_md.resolve_root(args))
    if refusal:
        print(refusal, file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
