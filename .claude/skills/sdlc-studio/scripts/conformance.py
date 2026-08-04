#!/usr/bin/env python3
"""SDLC Studio lifecycle-conformance check.

Asserts each unit (story) passed through the required lifecycle stages -
decomposed (an Epic link), specified (at least one AC), verifiable (a `Verify:`
line), and for Done stories: verified (AC marked `Verified: yes/manual`),
reconciled (no index drift, via reconcile), and critiqued (a committed APPROVE from
a critic whose reviewer id differs from the unit's author id, via critic.py). The
critic stage is an independence gate: a self-review, or a verdict with no recorded
author, never clears Done - and that floor applies to generic workers too, not only
persona-framed ones. Exits non-zero on any non-conformant unit, so the sprint loop
cannot mark a unit Done with a stage silently skipped - including skipping the critic
or self-reviewing it.

A stage a project has WAIVED through the decisions log (`decisions.py waive --subject
rule:conformance:<stage>[:<unit-or-range>]`) is reported as waived, naming the decision,
rather than counted as a fault: the lane's own remedy text recommends a waiver, so a waiver
it could not read made the gate recommend a no-op. The waiver is read from the log and is
therefore independent of any diff scope, because a close runs on a clean tree and that is
exactly when it is needed. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md, tiers  # noqa: E402
import reconcile  # noqa: E402  (sibling scripts; scripts dir is on sys.path)
import critic  # noqa: E402
import decisions  # noqa: E402  (the recorded waivers: a rule the project waived is not a finding)
try:
    import carry_forward  # noqa: E402  (EP0113 review policy)
except ImportError:  # pragma: no cover
    carry_forward = None
import doc_coverage  # noqa: E402  (the `documented` stage)
try:
    import verify_ac  # noqa: E402  (stamp resolution; a green on a dead pointer is not one)
except ImportError:  # pragma: no cover - conformance must survive a partial install
    verify_ac = None

_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
# A bullet's fillable value: strip the leading marker (checkbox, **Label:**) -> group(1).
_BULLET_VAL = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(?:\*\*[^*]+\*\*:?\s*)?(.*)$")

# The lifecycle stages this check judges, in report order - its finding-kind vocabulary.
# Every stage here can appear in a unit's `missing` list, so the remediation registry
# (sdlc_md.REMEDIATION["conformance"]) must carry a hint for each; a guard derives its
# expected key set from this tuple, so registry and check cannot drift out of step. The
# first three apply to every story; the rest are required only once a story is Done.
ALWAYS_STAGES = ("decomposed", "specified", "verifiable")
#: Story statuses BEFORE the Definition-of-Ready bar: an ungroomed story needs only `decomposed`,
#: not the AC stages (specified/verifiable), so a fresh refine output with placeholder ACs is
#: conformant until it is groomed to Ready.
_PRE_GROOMED_STORY_STATUS = ("Proposed", "Draft")
DONE_STAGES = ("verified", "reconciled", "critiqued", "documented", "promoted")
STAGES = ALWAYS_STAGES + DONE_STAGES

#: The stages a diff-scoped run does NOT judge for a unit outside the diff. Both need an
#: expensive per-unit probe - `verified` resolves every recorded stamp against the test tree,
#: `critiqued` walks the critic and sign-off ledgers - and together they are the bulk of a
#: whole-workspace run's cost. A scoped-out unit records them as None ("not judged"), never as a
#: pass: a stage nobody examined must not read as one that cleared. Every other stage is derived
#: from the file's own text or from repo-wide facts already computed once, so it costs nothing
#: to keep judging and stays reported for every unit.
UNJUDGED_WHEN_SCOPED = ("verified", "critiqued")

#: The rules this lane honours a recorded waiver for, DERIVED from the stage vocabulary above:
#: one rule per stage, so a stage added to STAGES is waivable without a second list here
#: remembering to grow. `decisions.py` reads this to validate a waiver at record time, which is
#: the only reason an operator ever learns the spelling before the row is already inert.
WAIVABLE_RULES = tuple(f"conformance:{stage}" for stage in STAGES)
#: The decision-cell stem a waiver of this lane carries: `waiver: rule:conformance:<stage>[:scope]`.
WAIVER_SUBJECT_STEM = "rule:conformance:"


def _scope_covers(scope: str, rid: str) -> bool:
    """Whether a waiver's scope tail covers this unit.

    Three forms and no fourth: absent (the stage is waived for every unit), one normalised id,
    or an inclusive `<id>-<id>` range - the shape an inherited cohort actually has. A tail that
    resolves to none of them covers NOTHING, so a misspelled scope narrows to nobody rather
    than widening to everybody; the record-time refusal is what makes that visible.
    """
    if not scope:
        return True
    # The single-id reading is tried FIRST, because a v3 ULID id (`US-01JQK3F8`) contains the
    # same dash a range does: parsing for the range first would read that scope as a range from
    # `US` to `01JQK3F8`, resolve neither, and cover nothing - a waiver silently naming no unit,
    # on exactly the newest ids, which is the shape BG0318 already cost this gate once.
    if sdlc_md.norm_id(scope) == sdlc_md.norm_id(rid):
        return True
    lo, sep, hi = scope.partition("-")
    if sep:
        lo_n, hi_n, num = (sdlc_md.id_number(lo.strip()), sdlc_md.id_number(hi.strip()),
                           sdlc_md.id_number(rid))
        return None not in (lo_n, hi_n, num) and lo_n <= num <= hi_n
    return False


def scope_tail_error(scope: str) -> str | None:
    """Why a waiver's scope tail resolves to no unit, or None when it can resolve to one.

    The RECORD-time counterpart of `_scope_covers`, and derived from it rather than a second
    reading of the grammar: a tail this refuses is one `_scope_covers` could never match. The
    same three forms and no fourth - absent, one id, an inclusive `<id>-<id>` range.

    Without this, `rule:conformance:critiqued:pre-two-role` records clean and covers NOTHING:
    the rule half is validated, the tail is not, so a waiver that silently exempts nobody looks
    exactly like one that works. Worse than a refused waiver, because the gate it was meant to
    quiet stays red and the record says the question was settled.
    """
    if not scope:
        return None
    if sdlc_md.id_number(scope) is not None:
        return None
    lo, sep, hi = scope.partition("-")
    if sep and None not in (sdlc_md.id_number(lo.strip()), sdlc_md.id_number(hi.strip())):
        return None
    return (f"waiver scope {scope!r} names neither a unit nor an inclusive `<id>-<id>` range, "
            f"so it would cover no unit at all - a waiver that exempts nobody. Name the units "
            f"(e.g. `US0103-US0310`), or drop the scope tail to waive the stage outright")


def stage_waivers(root: Path | str) -> list[dict]:
    """Every ACCEPTED `rule:conformance:<stage>[:<scope>]` waiver, read once per run.

    Returns [{stage, scope, decision}]. A superseded or revisited waiver does not hold (that is
    `decisions.list_decisions`' own rule), and a subject naming something outside STAGES is not
    a waiver of this lane, so it is ignored here rather than guessed at.
    """
    stem = f"{decisions.WAIVER_PREFIX} {WAIVER_SUBJECT_STEM}"
    out: list[dict] = []
    for rec in decisions.list_decisions(root):
        if rec["status"] != "accepted":
            continue
        cell = rec["decision"].strip().lower()
        if not cell.startswith(stem):
            continue
        stage, _sep, scope = cell[len(stem):].partition(":")
        if stage in STAGES:
            out.append({"stage": stage, "scope": scope.strip(), "decision": rec["id"]})
    return out


def waived_stages(waivers: list[dict], rid: str, missing: list[str]) -> list[dict]:
    """The subset of `missing` this unit has a recorded waiver for, each naming its decision.
    Order follows `missing`, so the report reads in stage order however the log is written."""
    out: list[dict] = []
    for stage in missing:
        did = next((w["decision"] for w in waivers
                    if w["stage"] == stage and _scope_covers(w["scope"], rid)), None)
        if did:
            out.append({"stage": stage, "decision": did})
    return out


def _real(value: str | None) -> bool:
    """True when a line's fillable value has substance beyond a {{placeholder}}:
    a scaffold whose AC/Verify slots are still `{{...}}` is not yet specified. Punctuation
    or markdown left after stripping the placeholder is not substance (so `{{x}}.` is not
    real - this keeps conformance consistent with validate, which flags that line)."""
    residue = _PLACEHOLDER.sub("", value or "")
    return re.sub(r"[\s.,;:!?*_`>~\-]+", "", residue) != ""


def _ac_section(text: str) -> str:
    """The body under the story's `## Acceptance Criteria` heading, or ''."""
    out: list[str] = []
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if in_ac:
            out.append(line)
    return "\n".join(out)


def story_is_ungroomed(text: str) -> bool:
    """True when a story's Acceptance Criteria are a grooming placeholder rather than authored
    content.

    TWO SHAPES, not one. `refine` writes an explicit marker (`sdlc_md.UNGROOMED_AC_TOKEN`) today,
    but every story minted before that carries the bare `{{...}}` template scaffold instead. A
    count that knew only the marker reported ZERO ungroomed while 31 such stories sat in this
    workspace - confidently wrong in the safe direction, which is the failure mode this project
    ranks worst. The legacy shape is an AC section carrying a placeholder and NO authored
    criterion beside it; a groomed story that merely quotes `{{...}}` in its prose still has a
    real criterion, so it is not caught here.

    The count is what makes a refined backlog's outstanding grooming machine-visible: an operator
    sees how much a batch still owes before planning it, instead of meeting a full-batch refusal
    at plan time."""
    if sdlc_md.UNGROOMED_AC_TOKEN in text:
        return True
    section = _ac_section(text)
    if not _PLACEHOLDER.search(section):
        return False
    has_real_ac, _, _ = _ac_signals(text)
    return not has_real_ac


def unit_is_ungroomed(type_: str, text: str) -> tuple[bool, str]:
    """Whether a unit of ANY type still owes grooming, and in one word why. THE one definition.

    Three shapes, each with a different fix, so the reason is returned rather than folded into a
    bare boolean:

    - `no-criteria`   - no `## Acceptance Criteria` content at all. Asked of `validate._has_criteria`,
      the SAME predicate `transition` consults, so the planner and the deliverer cannot disagree
      about identical bytes - they did, and a batch was planned in which 21 of 58 points could
      not reach a terminal status.
    - `placeholder`   - the `refine` marker or the bare `{{...}}` scaffold, story-shaped.
    - `derived-only`  - every criterion is one `file_finding` wrote from the finding's own prose.
      This is the shape that reads like content and is not; it passed every check in the repo.

    Type-agnostic on purpose. The predecessor asked only about stories, on the reasoning that
    "a bug carries no user-story scaffold" - true of the scaffold, and false of the other two
    shapes, which is how nine bugs reached a plannable batch unjudgeable."""
    # SCOPED TO THE TYPES THE DELIVERER ASKS. `transition` demands criteria only where
    # `executes_verifiers` holds - story and bug - so applying the demand to every type made the
    # planner refuse what the deliverer admits, which is the same drift in the opposite
    # direction. It refused 57 of 57 RFCs and 114 of 207 epics on this tree, with a message
    # ("a terminal status will refuse it") that was false for all of them: `transition
    # CR0001 -> Complete` succeeds. The criteria question is asked of exactly the types that
    # answer for criteria.
    if sdlc_md.executes_verifiers(type_):
        try:
            import validate as _validate  # noqa: PLC0415 - deferred; one predicate, never a second
            has_criteria = _validate._has_criteria(text)
        except Exception:  # noqa: BLE001 - matches the deliverer's own construct at
            # `transition.py`: an unimportable validator leaves the demand unenforced rather than
            # failing every batch. It IS a fail-open, and it is the same fail-open on both sides,
            # which is the property that matters here - a guard the two ends disagree about is
            # worse than one they are both missing.
            has_criteria = True
        if not has_criteria:
            return True, "no-criteria"
    if story_is_ungroomed(text):
        return True, "placeholder"
    # NOT wrapped in a bare except. The first draft was, and the import inside it failed - the
    # leg was inert while every other test in the class passed, which is the shape this whole
    # unit exists to catch. An unimportable writer is a broken install, not a groomed batch.
    import file_finding as _ff  # noqa: PLC0415 - the writer owns the shape it writes
    if _ff.criteria_are_all_derived(text):
        return True, "derived-only"
    return False, ""


def carry_forward_covers(root, review, findings) -> bool:
    """EP0113: under the carry-forward policy a sprint-level REJECT does not block the close,
    provided every finding is filed or explicitly waived. Returns True when the REJECT is
    carried; raises carry_forward.PolicyError (via validate) when a finding is unhandled, so
    the close learns WHY it still blocks. False (blocks) under the default block policy or when
    carry_forward is unavailable."""
    if carry_forward is None or not review:
        return False
    if (review.get("verdict") or "").upper() != critic.REJECT:
        return False
    return carry_forward.reject_carries_forward(root, findings)



def _ac_signals(text: str) -> tuple[bool, bool, list[str]]:
    """Scan a story body once for the (specified, verifiable, verified-states) signals: whether
    it declares an AC, a Verify line, and the list of `- **Verified:**` states."""
    has_ac = has_verify = False
    in_ac = False
    verified_states: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        # The refine ungroomed-AC marker is an explicit placeholder, not authored content: it
        # must not read as a specified criterion. Skip it, so an ungroomed refined story stays
        # unspecified (and `story_is_ungroomed` counts it) rather than looking groomed.
        if in_ac and sdlc_md.UNGROOMED_AC_TOKEN in line:
            continue
        hm = sdlc_md.AC_HEADING_RE.match(line)
        bm_ac = sdlc_md.AC_BULLET_RE.match(line)
        if hm and _real(hm.group(2)):
            has_ac = True
        elif bm_ac and _real(bm_ac.group(2)):
            has_ac = True
        # A populated Acceptance Criteria section counts as "specified" even when the
        # ACs are prose bullets without an ACn id (house templates) - but a line whose
        # fillable value is only a {{placeholder}} does not count.
        elif in_ac and line.strip() and not line.startswith("#"):
            bm = _BULLET_VAL.match(line)
            if _real(bm.group(1) if bm else line):
                has_ac = True
        vm = sdlc_md.VERIFY_RE.match(line)
        if vm and _real(vm.group(2)):
            has_verify = True
        m = sdlc_md.VERIFIED_RE.match(line)
        if m:
            verified_states.append(m.group(2).lower())
    return has_ac, has_verify, verified_states


#: The named halves `critiqued` composes. Reporting the composite alone told an operator a
#: gate was unmet without saying which of up to three independent conditions it wanted, so
#: the answer was reachable only by reading this function. Each unmet half is named instead.
HALF_VERDICT = "independent APPROVE verdict"
HALF_EVIDENCE = "adversarial-pass evidence"
HALF_SIGNOFF = "reviewer-of-record sign-off"


def two_role_applies_to(rid: str, two_role_cutoff: int | None) -> bool:
    """Whether the two-role review requirement covers this unit.

    `review.two_role_after` is a SEQUENTIAL cutoff, and `id_number` has no number to give for
    a v3 short-ULID id. Treating that None as "before the cutoff" stood the gate down for
    every ULID unit - the newest work in the workspace, and precisely what a forward-only
    cutoff exists to cover. An unnumbered id is by construction later than any sequential
    one, so it fails CLOSED: no number means the gate applies. Unset cutoff still means the
    requirement applies to nobody, so a project that never configured it is untouched.
    """
    if two_role_cutoff is None:
        return False
    rid_num = sdlc_md.id_number(rid)
    return rid_num is None or rid_num > two_role_cutoff


def verdict_half_ok(root, rid, sprint_covers: bool) -> bool:
    """Whether the VERDICT half of `critiqued` is satisfied - THE one definition.

    Three ways, and they are the same three everywhere this question is asked:

      * an independent (or grandfathered pre-gate) APPROVE;
      * a REJECT whose every raised finding carries a recorded closure - the rejection was
        answered, which is what the gate is actually asking;
      * no per-unit verdict at all, but a batch review covering the unit.

    Extracted because this file computed it TWICE - once in `critiqued_unmet` and once in the
    detailed form below - and teaching only the first about repaired rejections left nine Done
    units reporting `missing critiqued` while the other answer said they were fine. That is the
    drift `critiqued_unmet`'s own docstring exists to warn about, reproduced inside the file
    that warns about it.
    """
    verdict = critic.verdict_for(root, rid)
    per_unit_ok = (bool(verdict) and verdict["verdict"] == critic.APPROVE
                   and (critic.is_independent(verdict) or critic.is_pre_gate(verdict)))
    if per_unit_ok:
        return True
    if verdict and str(verdict.get("verdict") or "").upper() == critic.REJECT:
        return critic.repair_state(root, rid)["state"] == "complete"
    return verdict is None and sprint_covers


def critiqued_unmet(root, rid, two_role_cutoff: int | None,
                    critic_required: bool = True, two_role_only: bool = False) -> list[str]:
    """The `critiqued` halves left unmet for `rid`, in this module's own vocabulary.

    THE authority for the Done review bar, so the lane and the VERB that writes `Status: Done`
    ask one question and get one answer. `transition.py` first re-implemented these halves
    inline against `critic.*` with its own strings while claiming in its docstring to delegate
    "the predicate AND the vocabulary" - and the copy was WEAKER than this one, omitting the
    verdict half entirely, so a story reached Done with no independent APPROVE recorded and the
    lane then marked it non-conformant. Two answers to one question is the drift the docstring
    said it was avoiding.
    """
    verdict = critic.verdict_for(root, rid)
    sprint_covers = critic.sprint_covers_independently(
        root, rid, critic.sprint_review_for(root, rid))
    verdict_ok = verdict_half_ok(root, rid, sprint_covers)
    unmet = []
    # `two_role_only` is for the callers that enforce the TWO-ROLE clause specifically - the
    # Done verb, whose bar is that clause. The verdict half is the `critiqued` stage's own
    # concern and is enforced by this lane; a verb that also demanded it would refuse work this
    # lane accepts, which is the same two-answers-to-one-question defect pointing the other way.
    # The vocabulary is shared either way, which is what stops the two drifting.
    if critic_required and not verdict_ok and not two_role_only:
        unmet.append(HALF_VERDICT)
    if two_role_applies_to(rid, two_role_cutoff):
        if not (bool(critic.evidence_for(root, rid)) or sprint_covers):
            unmet.append(HALF_EVIDENCE)
        if not critic.is_independent_signoff(root, rid, critic.signoff_for(root, rid)):
            unmet.append(HALF_SIGNOFF)
    return unmet


def _done_stages(root, rid, verified_states, no_index, drift_ids, doc_ok,
                 two_role_cutoff=None, critic_required=True, dead_stamps=0) -> tuple:
    """The four Done-only conformance stages (verified, reconciled, critiqued, documented),
    plus the list of `critiqued` halves left unmet.

    The critiqued stage composes its two halves independently, so a story DoD that
    downgrades ONE of them never disarms the other: the verdict half (independent
    APPROVE) applies while `critic_required`; the two-role half (evidence + an
    independent reviewer-of-record sign-off) applies for units past `two_role_cutoff`.

    Every APPLICABLE half is evaluated, never short-circuited on the first failure, because
    an operator told only the first of three owed conditions repairs one and meets the gate
    again. Halves that do not apply to this unit are not reported unmet either: naming an
    inapplicable condition is the same misdirection pointing the other way.
    """
    # A stamp is evidence only while the thing it points at still exists. `dead_stamps`
    # counts ACs recorded green whose verifier now selects NOTHING - a `-k` pattern matching
    # no test, or a node address whose class is gone. One such stamp read green for two days
    # while the test it named did not exist, because freshness compares the AC TEXT and the
    # text had not changed. A green resting on a dead pointer is not verification.
    verified = (bool(verified_states)
                and all(v in ("yes", "manual") for v in verified_states)
                and dead_stamps == 0)
    reconciled = (not no_index) and sdlc_md.norm_id(rid) not in drift_ids
    verdict = critic.verdict_for(root, rid)
    # A sprint-level adversarial full-diff review covers every unit in its range at once. It
    # satisfies `critiqued` for a unit that had no INDIVIDUAL verdict - but never overrides a
    # per-unit REJECT, which still repairs per unit.
    sprint_rev = critic.sprint_review_for(root, rid)
    sprint_covers = critic.sprint_covers_independently(root, rid, sprint_rev)
    # The verdict half: an APPROVE AND proven author != reviewer independence - a
    # self-review (or a verdict with no recorded author) never clears the Done gate. The floor
    # holds for generic workers too. Units closed before the gate (the visible PRE_GATE marker,
    # under the prior risk-scaled policy) are grandfathered; the gate applies to all new work.
    # THE shared definition - see `verdict_half_ok`. A batch-level APPROVE never papers over a
    # per-unit REJECT; only a recorded, complete REPAIR answers one.
    verdict_ok = verdict_half_ok(root, rid, sprint_covers)
    verdict_half = verdict_ok if critic_required else True
    # The two-role half: with `review.two_role_after` set, a Done unit PAST the cutoff
    # additionally needs the adversarial pass recorded as EVIDENCE and an independent
    # reviewer-of-record SIGN-OFF (principal != author and not an authoring-session
    # subagent - re-checked here as the backstop to record_signoff's write-time
    # refusal). Forward-only: pre-cutoff units and projects without the config keep
    # today's behaviour byte-for-byte.
    two_role_applies = two_role_applies_to(rid, two_role_cutoff)
    evidence_half = signoff_half = True
    if two_role_applies:
        # The evidence half is satisfied by a per-unit adversarial pass OR a sprint-level
        # review covering this unit; the independent reviewer-of-record sign-off is still
        # required per unit (the sprint pass is evidence, not the principal's sign-off).
        evidence_half = bool(critic.evidence_for(root, rid)) or sprint_covers
        signoff_half = critic.is_independent_signoff(root, rid, critic.signoff_for(root, rid))
    # Conjunction of the same three conditions the short-circuiting form computed, so the
    # verdict is unchanged; only the reporting gains detail.
    critiqued = verdict_half and evidence_half and signoff_half
    unmet = []
    if critic_required and not verdict_half:
        unmet.append(HALF_VERDICT)
    if two_role_applies and not evidence_half:
        unmet.append(HALF_EVIDENCE)
    if two_role_applies and not signoff_half:
        unmet.append(HALF_SIGNOFF)
    return verified, reconciled, critiqued, doc_ok, unmet


def changed_story_ids(root: Path) -> set[str] | None:
    """Normalised ids of the story files this working tree has changed against HEAD.

    None when the git probe cannot answer - UNKNOWN, never "none changed". The caller judges
    the whole workspace on None, because a scope built from an unanswered probe would judge
    nothing and print a clean count over an unexamined tree.
    """
    import gate  # the family's one git changed-file idiom; a second copy would drift from it
    names = gate.changed_paths(str(root))
    if names is None:
        return None
    if not names:
        # AN EMPTY DIFF IS NOT AN EMPTY SCOPE. A clean checkout - CI, a deploy preflight, a close
        # preflight - has nothing changed, so there is nothing to narrow TO; scoping there judged
        # ZERO units and printed PASS over an unexamined workspace. Measured: a story committed
        # with `Status: Bananas`, tree clean, `gate.py --root .` -> gate: PASS, where the same
        # tree failed before scoping existed. Nothing to scope means judge everything, exactly as
        # an unanswerable probe does.
        return None
    rel, _prefix = sdlc_md.ARTIFACT_TYPES["story"]
    base = (Path(root) / rel).resolve()
    out: set[str] = set()
    for name in names:
        path = (Path(root) / name).resolve()
        if path.parent != base or path.name == "_index.md":
            continue
        rid = sdlc_md.extract_record_id(path.stem)
        if rid:
            out.add(sdlc_md.norm_id(rid))
    return out


def detect_conformance(repo_root: Path | str, changed: bool = False,
                       scope_ids: "set[str] | None" = None) -> dict:
    """Per-story lifecycle conformance.

    Returns {"units": [{id, type, status, stages, conformant, missing}],
    "summary": {total, conformant, nonconformant}}. A story is conformant when
    every required stage for its status is present.

    `changed` narrows the PER-UNIT ledger to the stories this working tree touched: a unit
    outside the diff is still reported, with everything cheap about it still judged, but it is
    not charged to the `nonconformant` count that decides the exit code. The narrowing stops
    there. Repo-global stages are computed over the whole tree and still counted under
    `global_failures`, so scoping cannot become a way to hide one, and a git probe that cannot
    answer falls back to judging everything rather than to an empty scope.
    """
    root = Path(repo_root)
    changed_ids = changed_story_ids(root) if changed else None
    degraded = bool(changed) and changed_ids is None
    # An explicit batch scope (the sprint close passes the run's own units) narrows the per-unit
    # ledger to exactly those ids, TAKING PRECEDENCE over the diff scope: a clean tree has no diff
    # to narrow to, so the close needs the batch to say which units it OWNS rather than judging the
    # whole workspace and blocking on a different author's debt. An EMPTY scope charges nothing
    # per-unit - it is not "judge everything" (that is what an unanswerable probe means, above) -
    # so a bug-only batch owns no story unit. The repo-global stages stay at full strength either
    # way, so scoping can never hide a repo-wide failure.
    narrow = ({sdlc_md.norm_id(x) for x in scope_ids} if scope_ids is not None else changed_ids)
    vocab = sdlc_md.status_vocab("story", root)
    # Adoption cutoff: a project that turns the gate on partway can set
    # `conformance.adopt_after: US0360` (or the bare `360`) in .config.yaml so units up
    # to and including that id are exempt (reported, not judged) - the discipline applies
    # forward, not retroactively. parse_cutoff accepts both spellings and raises loud on a
    # typo rather than silently dropping the cutoff.
    cutoff_num = sdlc_md.parse_cutoff(sdlc_md.project_override(root, "conformance.adopt_after"))
    # The two-role review gate's own forward-only cutoff: units past it need
    # evidence + independent sign-off to clear `critiqued`. Unset = old rule everywhere.
    two_role_cutoff = sdlc_md.parse_cutoff(sdlc_md.project_override(root, "review.two_role_after"))
    # The story-level Definition of Done, when the project declares one, decides which
    # review stages are REQUIRED: a DoD without `review.critic-approve` downgrades the
    # critic stage to human judgement (reported per unit, never silent); one without
    # `review.two-role` stands the sign-off requirement down even under the cutoff.
    story_dod = sdlc_md.dor_dod_level_checks(root, "done", "story")
    critic_required = story_dod is None or "review.critic-approve" in story_dod
    if story_dod is not None and "review.two-role" not in story_dod:
        two_role_cutoff = None
    dod_downgrades = [] if story_dod is None else sorted(
        c for c in ("review.critic-approve", "review.two-role") if c not in story_dod)
    # A story is "reconciled" only if its index row matches and exists: a drifted
    # status (status-mismatch) or a story absent from the index (missing-row) both
    # fail it, and a missing index file fails every story.
    _drift = reconcile.detect_type("story", root)["drift"]
    _no_index = any(d["kind"] == "missing-index" for d in _drift)
    drift_ids = {sdlc_md.norm_id(d["id"]) for d in _drift
                 if d.get("id") and d["kind"] in ("status-mismatch", "missing-row")}
    # Repo-global doc-coverage - the `documented` stage, like `reconciled`.
    _doc = doc_coverage.check(root)
    _doc_ok = _doc["ok"]
    # The stages whose failure is a property of the REPOSITORY, not of any one unit. Each is
    # reported once, with its own remedy, instead of being charged to every judged unit.
    globals_: list[dict] = []
    if not _doc_ok:
        # NAME the undocumented items. The finding already carries them, so telling the
        # operator to go and run `doc_coverage.py` to learn what this run had in hand was a
        # source dive charged for information the check had already computed.
        gaps = [f["name"] for f in _doc["findings"] if f["blocking"]]
        globals_.append({
            "stage": "documented",
            "reason": f"doc-coverage reports {len(gaps)} undocumented item(s): {_elide(gaps)}",
            "remedy": "catalogue each named item (a command in `help/help.md`, a script in "
                      "`reference-scripts*.md`); `doc_coverage.py --format json` gives the "
                      "full detail per finding",
        })
    if _no_index:
        globals_.append({
            "stage": "reconciled",
            "reason": "the story index is missing",
            "remedy": "run `reconcile.py apply` to rebuild the index from the file census",
        })
    global_failed = {g["stage"] for g in globals_}
    # The recorded waivers, read ONCE for the run. A rule the project waived through the
    # sanctioned path is not a finding: the lane's own remedy text recommends a waiver, so a
    # waiver that cleared nothing made the gate recommend a no-op. Independent of the diff
    # scope, because a close runs on a clean tree and that is exactly when it is needed.
    waivers = stage_waivers(root)
    units: list[dict] = []
    ok = 0
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        decomposed = sdlc_md.extract_field(text, "Epic") is not None
        has_ac, has_verify, verified_states = _ac_signals(text)
        scoped_out = narrow is not None and sdlc_md.norm_id(rid) not in narrow
        verified = reconciled = critiqued = documented = promoted = None
        critiqued_missing: list[str] = []
        if status == "Done" and scoped_out:
            # Outside the diff: judge only what is already computed or free to derive. The
            # repo-global stages MUST still be judged here - they are what a global failure is
            # attributed from, and skipping them would make a scoped run drop the very
            # repo-wide finding that has to survive the narrowing.
            reconciled = (not _no_index) and sdlc_md.norm_id(rid) not in drift_ids
            documented = _doc_ok
        elif status == "Done":
            dead = len(verify_ac.unresolvable_stamps(path, root)) if verify_ac else 0
            verified, reconciled, critiqued, documented, critiqued_missing = _done_stages(
                root, rid, verified_states, _no_index, drift_ids, _doc_ok,
                two_role_cutoff=two_role_cutoff, critic_required=critic_required,
                dead_stamps=dead)
        if status == "Done":
            # The backstop to the transition gate. That gate guards the tool path; a
            # hand-edited `Status: Done` walks round it, and the story is then Done without
            # the sections the tier deferred. Same doubling the AC-verify gate already has
            # (transition refuses it; `verified` re-checks it here).
            #
            # Shares ONE authority with the gate (lib.tiers), so the two cannot disagree: an
            # unknown tier fails closed, a `full` claim is checked against the sections rather
            # than believed, and an unstamped story - every artefact predating the tier - is
            # promoted by definition unless the project sets quality.require_full_sections.
            promoted = tiers.promotion_deficit(
                text, "story", strict=tiers.require_full_sections(root)) is None
        stages = {
            "decomposed": decomposed,
            "specified": has_ac,
            "verifiable": has_verify,
            "verified": verified,
            "reconciled": reconciled,
            "critiqued": critiqued,
            "documented": documented,
            "promoted": promoted,
        }
        # `decomposed` is required of every story; `specified` + `verifiable` are the
        # Definition-of-Ready bar, so an ungroomed story (Proposed/Draft - a fresh refine output
        # whose ACs are still placeholders) is conformant on `decomposed` alone. The AC stages
        # apply once it is Ready or beyond, so a large refined backlog does not read as
        # non-conformant before it is groomed.
        required = ["decomposed"]
        if status not in _PRE_GROOMED_STORY_STATUS:
            required += ["specified", "verifiable"]
        if status == "Done":
            required += list(DONE_STAGES)
            # `critiqued` stays required while EITHER half applies: the two-role
            # requirement (an armed cutoff) survives a critic-approve downgrade -
            # dropping one tag must never disarm both.
            two_role_applies = two_role_applies_to(rid, two_role_cutoff)
            if not critic_required and not two_role_applies:
                required.remove("critiqued")
        if scoped_out:
            # A stage this run did not examine cannot be required of the unit: requiring it
            # would report an untouched unit as missing a stage nobody looked at, which is the
            # mirror image of the failure the scope exists to avoid.
            required = [s for s in required if s not in UNJUDGED_WHEN_SCOPED]
        rid_num = sdlc_md.id_number(rid)
        exempt = cutoff_num is not None and rid_num is not None and rid_num <= cutoff_num
        all_missing = [] if exempt else [s for s in required if not stages[s]]
        # A waived stage is REPORTED as waived, naming the decision, and is not charged as a
        # fault. Applied before the global/per-unit split, so waiving a repo-wide stage clears
        # it the same way; an exempt unit has nothing to waive.
        waived = waived_stages(waivers, rid, all_missing)
        if waived:
            done_by = {w["stage"] for w in waived}
            all_missing = [s for s in all_missing if s not in done_by]
        # A repo-GLOBAL failure is one fact about the repository, not a defect in each unit.
        # Fanned per unit it reads as "118 broken units" when it is one uncatalogued command,
        # burying every genuine per-unit finding in the noise. Attribute it once (see
        # `globals` below) and keep it out of the unit's own ledger.
        # exempt units are not judged, so a global condition costs them nothing
        missing_global = [] if exempt else [s for s in all_missing if s in global_failed]
        missing = [s for s in all_missing if s not in global_failed]
        conformant = not missing
        ok += int(conformant and not exempt and not scoped_out)
        units.append({
            "id": rid,
            "type": "story",
            "status": status,
            "stages": stages,
            "exempt": exempt,
            # Outside this run's diff: reported in full, but advisory - its faults are not
            # charged to the count that decides the exit code. False on a whole-workspace run.
            "scoped_out": scoped_out,
            "conformant": conformant,
            # Machine-visible grooming debt: a refined story whose ACs are still the placeholder
            # marker, so an operator can count how much a refined backlog owes before planning it.
            "ungroomed": story_is_ungroomed(text),
            "missing": missing,
            # The stages a recorded decision waived, each naming the decision that waived it -
            # so waived debt reads as waived-and-attributable, never as silently absent.
            "waived": waived,
            # Which of `critiqued`'s halves are owed. Empty when the stage is satisfied, not
            # required, or not judged - so a reader never has to infer it from the composite.
            "critiqued_missing": critiqued_missing if "critiqued" in missing else [],
            "missing_global": missing_global,
            "downgraded": dod_downgrades if status == "Done" else [],
        })
    units.sort(key=lambda u: u["id"])
    # A repo-wide condition is only a FAILURE if it actually cost a judged unit its
    # conformance. Reporting one that affects nobody (a missing index in a repo with no Done
    # stories) would newly fail checks that legitimately passed before - attributing a
    # failure differently must not invent one.
    globals_ = [g for g in globals_
                if any(g["stage"] in u["missing_global"] for u in units)]
    total = len(units)
    exempt_n = sum(1 for u in units if u["exempt"])
    # Only a JUDGED unit's fault decides the exit code. A unit outside the diff is counted
    # separately as `advisory` so the two numbers can never be confused for one another.
    nonconformant = sum(1 for u in units if not u["conformant"] and not u["scoped_out"])
    advisory_n = sum(1 for u in units if not u["conformant"] and u["scoped_out"])
    judged_n = sum(1 for u in units if not u["scoped_out"])
    ungroomed_n = sum(1 for u in units if u["ungroomed"])
    # Units carrying at least one waived stage. Counted separately from `conformant`, so
    # waived debt is never invisible: the lane passes it and still says how much it passed.
    waived_n = sum(1 for u in units if u["waived"])
    # Waivers no judged unit carries. This lane's units are STORIES, so a waiver scoped to a
    # bug or a change request - or to nothing that resolves - produced no report line at all
    # and sat silently in force, which is exactly the outcome the report exists to prevent.
    attributed = {(w["stage"], w["decision"]) for u in units for w in (u["waived"] or [])}
    waivers_unattributed = [w for w in waivers
                            if (w["stage"], w["decision"]) not in attributed]
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "waivers_unattributed": waivers_unattributed,
        # Repo-wide failures, listed once. The gate counts these alongside per-unit
        # non-conformance, so attributing them once REPORTS better without enforcing less.
        "globals": globals_,
        # What this run narrowed itself to, and what it therefore did not judge. Always
        # present, so a reader never has to infer the scope from the numbers.
        "scope": {
            "changed": bool(changed),
            "degraded": degraded,
            "scoped_out_ids": [u["id"] for u in units if u["scoped_out"]],
            # The debt this run carried without judging - the scoped-out units that actually
            # have a fault, not every unit outside the diff. Same word, same meaning, as
            # `summary.advisory`: a report that spent one term on two counts would mislead.
            "advisory_ids": [u["id"] for u in units
                             if u["scoped_out"] and not u["conformant"]],
            "unjudged_stages": list(UNJUDGED_WHEN_SCOPED) if narrow is not None else [],
        },
        "summary": {"total": total, "conformant": ok,
                    "nonconformant": nonconformant, "exempt": exempt_n,
                    # The units this run actually judged, and the untouched ones it reported
                    # without charging - a scoped PASS is readable only alongside these two.
                    "judged": judged_n, "advisory": advisory_n,
                    # The refined backlog's outstanding grooming, countable rather than met at
                    # plan time: how many stories still carry the ungroomed-AC placeholder.
                    "ungroomed": ungroomed_n,
                    # Debt this lane passed on a recorded decision rather than on evidence.
                    "waived": waived_n,
                    "waived_unattributed": len(waivers_unattributed),
                    "global_failures": len(globals_)},
    }


# The two mechanisms that legitimately resolve a conformance failure, named inline at the
# gate so an operator does not have to already know they exist. Not the remediation
# per-stage hints (those are per-unit); these are the two whole-batch levers.
REMEDY_CUTOFF = ("set `conformance.adopt_after` in sdlc-studio/.config.yaml to grandfather "
                 "pre-adoption ids forward-only (accepts a bare id `103` or prefixed `US0103`; "
                 "ids <= it are exempt)")
REMEDY_BACKFILL = ("run `verify_ac` and back-annotate `- **Verified:**` to clear the "
                   "per-unit debt")


def _bulk_missed(result: dict) -> list[str]:
    """Stages that the bulk of judged units miss - the signal that this is an unadopted
    discipline / template shape (forward-only debt), not per-unit regressions. Mirrors the
    note in cmd_check so the gate and the CLI agree."""
    s = result["summary"]
    # Over the units this run JUDGED, so a diff-scoped run's shape is read against its own
    # denominator rather than against a whole workspace it did not examine.
    judged = s.get("judged", s["total"]) - s.get("exempt", 0)
    tally: dict[str, int] = {}
    for u in result["units"]:
        if not u["conformant"] and not u.get("scoped_out"):
            for m in u["missing"]:
                tally[m] = tally.get(m, 0) + 1
    return sorted(k for k, c in tally.items() if judged >= 3 and c >= 0.8 * judged)


def missing_detail(unit: dict) -> str:
    """A unit's missing stages, with `critiqued` expanded to the halves it actually owes.

    One line, every unmet half on it. `critiqued` alone reads as a single unmet condition
    when it is up to three, and which one is owed decides what the operator does next."""
    halves = unit.get("critiqued_missing") or []
    return ", ".join(f"critiqued ({', '.join(halves)})" if m == "critiqued" and halves else m
                     for m in unit["missing"])


def _elide(ids: list[str], limit: int = 3) -> str:
    """First `limit` ids then a count of the rest: a lane line stays readable without hiding
    how many it did not print."""
    return ", ".join(ids[:limit]) + (f", +{len(ids) - limit} more" if len(ids) > limit else "")


def scope_detail(result: dict) -> str:
    """What a diff-scoped run narrowed itself to, in one clause - empty on a whole-workspace
    run. A scoped verdict is only readable next to what it did NOT judge, so this names the
    denominator, the advisory units by id, the stages left unexamined, and the command that
    judges everything. A degraded probe says so and judges the whole workspace anyway."""
    scope = result.get("scope") or {}
    if not scope.get("changed"):
        return ""
    s = result["summary"]
    if scope.get("degraded"):
        return ("scope: there was no diff to scope to (a clean tree, or the git probe could not answer), so the WHOLE workspace "
                f"was judged ({s['judged']} unit(s))")
    out = f"scope: {s['judged']} of {s['total']} unit(s) judged (this diff)"
    untouched = scope.get("scoped_out_ids") or []
    ids = scope.get("advisory_ids") or []
    if untouched:
        out += f"; {len(untouched)} outside it not judged here"
        if ids:
            out += f", {len(ids)} of them carrying an advisory fault ({_elide(ids)})"
        out += f"; {', '.join(scope.get('unjudged_stages') or [])} not judged for those"
    return out + "; `--release` judges the whole workspace"


def remedy_detail(result: dict) -> str:
    """Gate-facing one-liner for a conformance failure: the bare count PLUS the two remedies
    (the adopt_after cutoff and the verify_ac backfill), and whether the shape reads as
    pre-existing unadopted-discipline debt (forward-only) rather than a fresh regression.
    Returns just the count when nothing is non-conformant."""
    n = result["summary"]["nonconformant"]
    # A repo-global failure is stated once, as itself. Before this, one uncatalogued command
    # rendered as "N non-conformant unit(s)" across the whole repo - a true count of a
    # misleading thing, which buried every genuine per-unit finding.
    gl = "; ".join(f"{g['stage']} (repo-wide): {g['reason']} - {g['remedy']}"
                   for g in result.get("globals", []))
    # The scope rides on the PASSING line too: a green count over a narrowed run must say how
    # narrow it was, or the narrowing becomes a silent way to report less than was checked.
    sc = scope_detail(result)
    # Debt this lane passed on a RECORDED DECISION rather than on evidence, said on the passing
    # line too. A gate that silently swallows a waiver is the mirror of a gate that cannot see
    # one: both leave an operator reading a number that does not mean what it says.
    wv = result["summary"].get("waived") or 0
    tail = ((f". Repo-wide: {gl}" if gl else "")
            + (f". {wv} unit(s) passed on a recorded waiver (sdlc-studio/decisions.md)"
               if wv else "")
            + (f". {sc}" if sc else ""))
    if not n:
        return f"{n} non-conformant unit(s)" + tail
    bulk = _bulk_missed(result)
    if bulk:
        nature = (f"most miss {', '.join(bulk)} - likely unadopted-discipline debt "
                  "(pre-existing, forward-only), not a regression from this change")
    else:
        nature = "scattered per-unit gaps - check whether this change regressed them"
    # Same aiming rule as the CLI: the backfill lever is named only when the stage it clears
    # is one of the stages actually missing, so the gate line cannot point at the wrong gate.
    misses_verified = any("verified" in u["missing"] for u in result["units"]
                          if not u["conformant"] and not u.get("scoped_out"))
    remedies = REMEDY_CUTOFF + (f"; or {REMEDY_BACKFILL}" if misses_verified else "")
    base = f"{n} non-conformant unit(s): {nature}. Remedies: {remedies}"
    return base + tail


def cmd_check(args: argparse.Namespace) -> int:
    """Run the conformance check; exit non-zero if any unit is non-conformant."""
    result = detect_conformance(sdlc_md.resolve_root(args), changed=getattr(args, "changed", False))
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        extra = f", {s['exempt']} exempt (pre-adoption)" if s.get("exempt") else ""
        print(f"conformance: {s['conformant']}/{s['total']} conformant, {s['nonconformant']} not{extra}"
              " (story-scoped: a bug/CR tranche relies on the critic + gate)")
        # What the run narrowed itself to, said before any verdict is read - never inferred.
        sc = scope_detail(result)
        if sc:
            print(f"  {sc}")
        if s.get("ungroomed"):
            print(f"  {s['ungroomed']} story(ies) still carry the refine ungroomed-AC placeholder "
                  "- groom them (author real ACs and a Verify line) before planning to Done")
        # Repo-wide failures first, once each, with the count of units they would otherwise
        # have been charged to - so the operator sees "one doc gap", not "118 broken units".
        for g in result.get("globals", []):
            affected = sum(1 for u in result["units"] if g["stage"] in u.get("missing_global", []))
            print(f"  REPO-WIDE {g['stage']}: {g['reason']} "
                  f"(would otherwise report against {affected} unit(s))")
            print(f"    fix: {g['remedy']}")
        downgrades = next((u["downgraded"] for u in result["units"]
                           if u.get("downgraded")), [])
        if downgrades:
            print(f"  downgraded to human-judged by definition-of-done.md (tag removed): "
                  f"{', '.join(downgrades)}")
        # Waived debt, named with the decision that waived it. Printed BEFORE the findings and
        # never folded into them: an operator reading a clean lane must still see what the lane
        # passed on a decision rather than on evidence, and be able to go and read that decision.
        # Grouped by (stage, decision) with the ids elided, because one inherited cohort is one
        # fact - printed per unit it buries the findings it sits above.
        waived_groups: dict[tuple, list[str]] = {}
        for u in result["units"]:
            for w in u.get("waived", []):
                waived_groups.setdefault((w["stage"], w["decision"]), []).append(u["id"])
        for (stage, did), ids in sorted(waived_groups.items()):
            print(f"  WAIVED {stage}: {len(ids)} unit(s) by {did} "
                  f"({_elide(ids)}) - see sdlc-studio/decisions.md")
        # A waiver this lane's units do not carry is still IN FORCE. The per-unit report above
        # is built from stories, so a waiver scoped to a bug or a change request - or one whose
        # scope resolves to nothing at all - produced no line, and a rule the project waived sat
        # silently active. That is the outcome the waiver report exists to prevent, so an
        # unattributed waiver is named rather than omitted.
        for row in result.get("waivers_unattributed") or []:
            print(f"  WAIVED {row['stage']}: in force by {row['decision']}, scoped to "
                  f"{row['scope'] or 'every unit'} - NOT carried by any unit this lane judges "
                  f"(it judges stories), so it is reported here rather than left silent")
        tally: dict[str, int] = {}
        for u in result["units"]:
            if not u["conformant"]:
                # An untouched unit is still NAMED, marked as what it is: reported, not judged.
                mark = "ADVISORY (outside this diff) " if u.get("scoped_out") else ""
                print(f"  {mark}{u['id']} ({u['status']}): missing {missing_detail(u)}")
                if u.get("scoped_out"):
                    continue  # advisory faults do not steer this run's guidance
                for m in u["missing"]:
                    tally[m] = tally.get(m, 0) + 1
        hints = sdlc_md.remediation_lines("conformance", tally)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
            bulk = _bulk_missed(result)
            if bulk:
                print(f"  note: most units miss {', '.join(bulk)} - likely an unadopted "
                      "discipline or template shape, not per-unit drift; adopt it or scope conformance.")
            # The two whole-batch levers, named so the operator need not already know them.
            # The backfill lever clears the VERIFIED stage and nothing else, so it is offered
            # only when a unit actually misses that stage. Printed under a missing-critiqued
            # failure it aimed the operator at a gate that was already green.
            print(f"  remedy: {REMEDY_CUTOFF}")
            if "verified" in tally:
                print(f"  remedy: {REMEDY_BACKFILL}")
    # A repo-wide failure is still a failure: attributing it once must not make it exit clean.
    return 1 if (result["summary"]["nonconformant"]
                 or result["summary"].get("global_failures")) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio lifecycle-conformance check.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Check each story passed the required lifecycle stages.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--changed", action="store_true",
                   help="Judge only the stories this working tree touched (staged, unstaged or "
                        "untracked). Untouched units are still reported, as advisory; the "
                        "repo-wide stages still run and still fail. With no git answer the "
                        "whole workspace is judged")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the same
    # tree. Resolving it at only one call site let the two disagree - the resolved value
    # guarded the run while each verb still wrote through a bare `--root .`, so a run
    # from a subdirectory acted on a stray workspace beside the cwd and exited 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
