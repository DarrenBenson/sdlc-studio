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
import json
import re
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
    """Parse a `YYYY-MM-DDTHH:MM:SSZ` verify-report timestamp to a UTC epoch, or None."""
    if not value:
        return None
    from datetime import datetime, timezone
    try:
        return datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc).timestamp()
    except (ValueError, TypeError):
        return None


def _story_has_executable_acs(text: str) -> bool:
    """True if the story declares any non-manual `Verify:` line (an executable AC). A story
    with only `manual` ACs (or none) has nothing the deterministic gate can check."""
    for line in text.splitlines():
        m = sdlc_md.VERIFY_RE.match(line)
        if m and m.group(2).strip().split(None, 1)[0].lower() not in ("manual", "manually"):
            return True
    return False


def _done_verify_gate(root: Path, path: Path, text: str) -> str | None:
    """Definition-of-Done safety net on the hand-driven path. A story may not reach
    Done with executable ACs that are red or never run - the 0/7 a hand-driving agent shipped.
    Returns a block reason, or None to allow. Manual-only / AC-less stories are never blocked;
    a green report passes. The hard gate is the one deterministic fact - the verifier result;
    critic semantic findings stay advisory (handled elsewhere)."""
    if not _story_has_executable_acs(text):
        return None  # nothing executable to verify
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


def _request_terminal_gate(root: Path, type_: str, artifact_id: str,
                           target_canon: str | None) -> str | None:
    """A REQUEST (CR/RFC) may not reach its SUCCESSFUL terminal by assertion (G2). A CR is
    Complete only when every story and epic it produced is resolved (in a terminal state); an RFC
    is Accepted only when every CR it produced is resolved. "Resolved" is terminal, not strictly
    Done: a child legitimately dropped (a Won't-Implement story, a Rejected child CR) does not
    force the parent onto --force. A childless request cannot be successfully terminal - it
    produced nothing, so it delivered nothing.

    Scoped to the successful terminal (Complete for a CR, Accepted for an RFC): a request the
    team decides NOT to build is still closable as Rejected / Superseded / Withdrawn without
    children, because that closure asserts no delivery. Returns a block reason, or None to allow.
    Overridable with --force, like the other close gates, but the sanctioned path is to finish or
    close the children first."""
    if not sdlc_md.is_request(type_):
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


def _pre_write_gates(root, artifact_id, new_status, type_, path, text,
                     target_canon, from_canon, force, dry_run, triaged_by) -> str | None:
    """Run the ordered pre-write gates (bug-depth, depth-parity, done-verify, triage,
    plan-review). Raise ValueError on a hard block; else return the accumulated advisory
    warning (or None). Behaviour-preserving extraction of the interleaved gate ladder."""
    gate_warn = None
    # Every unmet gate is COLLECTED and reported in one refusal - refusing one requirement
    # per attempt cost an agent a round-trip per gate (three attempts to close a v3 finding).
    blocks: list[str] = []
    if type_ == "bug" and not force and not dry_run:
        block = _bug_depth_gate(text, target_canon)
        if block:
            blocks.append(f"{block}. Override with --force")
    if type_ == "story" and not dry_run and target_canon == "Done":
        parity = _story_target_parity(text)
        if parity:
            # advisory by default (existing projects unaffected); a project opts
            # into refusal via `quality.depth_parity_gate: true`. Read via the
            # gracefully-degrading project_override so a PyYAML-less machine gets the
            # gate decision, not a config-loading crash.
            if sdlc_md.project_override(root, "quality.depth_parity_gate", False) and not force:
                blocks.append(f"{parity}. Override with --force")
            else:
                gate_warn = f"depth-parity advisory: {parity}"
    if type_ == "story" and not force and not dry_run and target_canon == "Done":
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
    # Overridable with --force, like the other close gates.
    if not force:
        block = _request_terminal_gate(root, type_, artifact_id, target_canon)
        if block:
            blocks.append(f"{block}. Override with --force")
    # The triage gate fires on any exit from `inbox` for a v3 finding, dry-run included: an
    # honest preflight must surface the same refusal a real run would (never a false green).
    block = _triage_gate(root, type_, text, from_canon, target_canon, triaged_by)
    if block:
        blocks.append(block)
    # Plan-review gate (US0090): a story with spec-derived ACs cannot REACH implementation
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
    if blocks:
        joined = "; AND ".join(blocks)
        raise ValueError(f"{artifact_id} -> {new_status} blocked ({len(blocks)} requirement(s), "
                         f"all listed): {joined}.")
    return gate_warn


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


def transition(repo_root: Path | str, artifact_id: str, new_status: str,
               dry_run: bool = False, force: bool = False,
               metrics: dict | None = None, triaged_by: str | None = None,
               triage_severity: str | None = None) -> dict:
    """Set `artifact_id`'s status to `new_status`, sync its index, and cascade the epic
    breakdown for a story. Returns {id, type, from, to, index_synced, epic}.

    A story moving to Done is gated on its AC-verify result: red or never-run
    executable ACs block the transition unless `force=True`. Scoped to stories - CR/epic/bug
    closures are unaffected. Manual-only / AC-less stories are never blocked."""
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
    result = {"id": sdlc_md.extract_record_id(path.stem), "type": type_,
              "from": current, "to": new_status, "index_synced": False, "epic": None,
              "warning": gate_warn}
    if dry_run:
        return result
    return _post_write_sync_and_record(root, type_, path, new_text, result, current,
                                       new_status, vocab, gate_warn, metrics)


def _print_result(res: dict, dry_run: bool) -> None:
    verb = "would set" if dry_run else "set"
    extra = f"; epic {res['epic']} breakdown updated" if res.get("epic") else ""
    print(f"{verb} {res['id']} {res['from']} -> {res['to']}"
          + ("" if dry_run else f" (index synced={res['index_synced']}{extra})"))
    if res.get("warning"):
        print(f"  warning: {res['warning']}")


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
    ids = sdlc_md.resolve_ids(args)
    if not ids:
        print("specify at least one id: --id (repeatable) or --ids as a comma list",
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
        if critic._id(reviewer) == critic._id(author):
            print("error: reviewer == author - independence is the floor; a self-review "
                  "never clears the critiqued gate, so nothing was written", file=sys.stderr)
            return 2
    results = []
    refused = 0
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
            if getattr(args, "depth", None) and not args.dry_run:
                annotate(args.root, aid, "Verification depth", args.depth)
            if reviewer and not args.dry_run:
                import critic
                critic.record_verdict(args.root, aid, args.verdict, reviewer, author)
            metrics = {k: v for k, v in {"iterations": _num(args.iterations),
                                         "wall_time_s": _num(args.wall_time_s),
                                         "critic_verdict": args.verdict}.items() if v is not None}
            res = transition(args.root, aid, args.status, dry_run=args.dry_run,
                             force=args.force, metrics=metrics,
                             triaged_by=args.triaged_by, triage_severity=args.triage_severity)
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transition an artifact's status + cascade.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set", help="Set an artifact's status and sync index + epic breakdown.")
    sdlc_md.add_ids_argument(s, help_="artifact id, e.g. CR0042 / US0023; repeat --id or pass "
                                      "--ids as a comma list for a same-target batch (each id is "
                                      "individually gated, one refusal never aborts the rest)")
    s.add_argument("--status", required=True, help="New status (must be in the type vocabulary)")
    s.add_argument("--root", default=".")
    s.add_argument("--iterations", help="run metric passed to the terminal-close telemetry event")
    s.add_argument("--wall-time-s", dest="wall_time_s", help="run metric for the telemetry event")
    s.add_argument("--verdict", help="critic verdict recorded on the telemetry event (and, with "
                                     "--reviewer/--author, in the critic log)")
    s.add_argument("--depth", help="one-call close: stamp `Verification depth` with this value "
                                   "before the gated transition (replaces a separate annotate)")
    s.add_argument("--reviewer", help="one-call close: record the critic verdict under this "
                                      "reviewer (must differ from --author)")
    s.add_argument("--author", help="one-call close: the authoring seat the reviewer judged "
                                    "(reviewer != author enforced before any write)")
    s.add_argument("--force", action="store_true",
                   help="bypass the story->Done AC-verify gate; recorded as an override")
    s.add_argument("--triaged-by", dest="triaged_by",
                   help="v3 triage: the triaging seat as `Name; type; version` (type is "
                        "human|persona|agent); required and recorded on an inbox->triaged "
                        "transition, must differ from the raiser (separation of duties)")
    s.add_argument("--triage-severity", dest="triage_severity",
                   help="v3 triage: the triager's severity, recorded alongside the raiser's")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_set)
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
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
