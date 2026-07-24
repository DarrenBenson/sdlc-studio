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
or self-reviewing it. Read-only; pure stdlib.
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


def _done_stages(root, rid, verified_states, no_index, drift_ids, doc_ok,
                 two_role_cutoff=None, critic_required=True, dead_stamps=0) -> tuple:
    """The four Done-only conformance stages (verified, reconciled, critiqued, documented).

    The critiqued stage composes its two halves independently, so a story DoD that
    downgrades ONE of them never disarms the other: the verdict half (independent
    APPROVE) applies while `critic_required`; the two-role half (evidence + an
    independent reviewer-of-record sign-off) applies for units past `two_role_cutoff`.
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
    per_unit_ok = (bool(verdict) and verdict["verdict"] == critic.APPROVE
                   and (critic.is_independent(verdict) or critic.is_pre_gate(verdict)))
    # Sprint coverage stands in ONLY when the unit has no per-unit verdict of its own: a recorded
    # per-unit REJECT is not papered over by a batch-level APPROVE.
    verdict_ok = per_unit_ok or (verdict is None and sprint_covers)
    critiqued = verdict_ok if critic_required else True
    # The two-role half: with `review.two_role_after` set, a Done unit PAST the cutoff
    # additionally needs the adversarial pass recorded as EVIDENCE and an independent
    # reviewer-of-record SIGN-OFF (principal != author and not an authoring-session
    # subagent - re-checked here as the backstop to record_signoff's write-time
    # refusal). Forward-only: pre-cutoff units and projects without the config keep
    # today's behaviour byte-for-byte.
    if critiqued and two_role_cutoff is not None:
        rid_num = sdlc_md.id_number(rid)
        if rid_num is not None and rid_num > two_role_cutoff:
            signoff = critic.signoff_for(root, rid)
            # The evidence half is satisfied by a per-unit adversarial pass OR a sprint-level
            # review covering this unit; the independent reviewer-of-record sign-off is still
            # required per unit (the sprint pass is evidence, not the principal's sign-off).
            has_evidence = bool(critic.evidence_for(root, rid)) or sprint_covers
            critiqued = has_evidence and critic.is_independent_signoff(root, rid, signoff)
    return verified, reconciled, critiqued, doc_ok


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


def detect_conformance(repo_root: Path | str, changed: bool = False) -> dict:
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
    _doc_ok = doc_coverage.check(root)["ok"]
    # The stages whose failure is a property of the REPOSITORY, not of any one unit. Each is
    # reported once, with its own remedy, instead of being charged to every judged unit.
    globals_: list[dict] = []
    if not _doc_ok:
        globals_.append({
            "stage": "documented",
            "reason": "doc-coverage reports at least one undocumented item",
            "remedy": "run `doc_coverage.py` to name the gap, then catalogue it "
                      "(a single uncatalogued command fails this stage repo-wide)",
        })
    if _no_index:
        globals_.append({
            "stage": "reconciled",
            "reason": "the story index is missing",
            "remedy": "run `reconcile.py apply` to rebuild the index from the file census",
        })
    global_failed = {g["stage"] for g in globals_}
    units: list[dict] = []
    ok = 0
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        decomposed = sdlc_md.extract_field(text, "Epic") is not None
        has_ac, has_verify, verified_states = _ac_signals(text)
        scoped_out = changed_ids is not None and sdlc_md.norm_id(rid) not in changed_ids
        verified = reconciled = critiqued = documented = promoted = None
        if status == "Done" and scoped_out:
            # Outside the diff: judge only what is already computed or free to derive. The
            # repo-global stages MUST still be judged here - they are what a global failure is
            # attributed from, and skipping them would make a scoped run drop the very
            # repo-wide finding that has to survive the narrowing.
            reconciled = (not _no_index) and sdlc_md.norm_id(rid) not in drift_ids
            documented = _doc_ok
        elif status == "Done":
            dead = len(verify_ac.unresolvable_stamps(path, root)) if verify_ac else 0
            verified, reconciled, critiqued, documented = _done_stages(
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
            rid_num_ = sdlc_md.id_number(rid)
            two_role_applies = (two_role_cutoff is not None and rid_num_ is not None
                                and rid_num_ > two_role_cutoff)
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
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
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
            "unjudged_stages": list(UNJUDGED_WHEN_SCOPED) if changed_ids is not None else [],
        },
        "summary": {"total": total, "conformant": ok,
                    "nonconformant": nonconformant, "exempt": exempt_n,
                    # The units this run actually judged, and the untouched ones it reported
                    # without charging - a scoped PASS is readable only alongside these two.
                    "judged": judged_n, "advisory": advisory_n,
                    # The refined backlog's outstanding grooming, countable rather than met at
                    # plan time: how many stories still carry the ungroomed-AC placeholder.
                    "ungroomed": ungroomed_n,
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
    tail = (f". Repo-wide: {gl}" if gl else "") + (f". {sc}" if sc else "")
    if not n:
        return f"{n} non-conformant unit(s)" + tail
    bulk = _bulk_missed(result)
    if bulk:
        nature = (f"most miss {', '.join(bulk)} - likely unadopted-discipline debt "
                  "(pre-existing, forward-only), not a regression from this change")
    else:
        nature = "scattered per-unit gaps - check whether this change regressed them"
    base = f"{n} non-conformant unit(s): {nature}. Remedies: {REMEDY_CUTOFF}; or {REMEDY_BACKFILL}"
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
        tally: dict[str, int] = {}
        for u in result["units"]:
            if not u["conformant"]:
                # An untouched unit is still NAMED, marked as what it is: reported, not judged.
                mark = "ADVISORY (outside this diff) " if u.get("scoped_out") else ""
                print(f"  {mark}{u['id']} ({u['status']}): missing {', '.join(u['missing'])}")
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
            print(f"  remedy: {REMEDY_CUTOFF}")
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
