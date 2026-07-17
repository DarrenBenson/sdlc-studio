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
import doc_coverage  # noqa: E402  (the `documented` stage)

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


def _real(value: str | None) -> bool:
    """True when a line's fillable value has substance beyond a {{placeholder}}:
    a scaffold whose AC/Verify slots are still `{{...}}` is not yet specified. Punctuation
    or markdown left after stripping the placeholder is not substance (so `{{x}}.` is not
    real - this keeps conformance consistent with validate, which flags that line)."""
    residue = _PLACEHOLDER.sub("", value or "")
    return re.sub(r"[\s.,;:!?*_`>~\-]+", "", residue) != ""


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
                 two_role_cutoff=None, critic_required=True) -> tuple:
    """The four Done-only conformance stages (verified, reconciled, critiqued, documented).

    The critiqued stage composes its two halves independently, so a story DoD that
    downgrades ONE of them never disarms the other: the verdict half (independent
    APPROVE) applies while `critic_required`; the two-role half (evidence + an
    independent reviewer-of-record sign-off) applies for units past `two_role_cutoff`.
    """
    verified = bool(verified_states) and all(v in ("yes", "manual") for v in verified_states)
    reconciled = (not no_index) and sdlc_md.norm_id(rid) not in drift_ids
    verdict = critic.verdict_for(root, rid)
    # The verdict half: an APPROVE AND proven author != reviewer independence - a
    # self-review (or a verdict with no recorded author) never clears the Done gate. The floor
    # holds for generic workers too. Units closed before the gate (the visible PRE_GATE marker,
    # under the prior risk-scaled policy) are grandfathered; the gate applies to all new work.
    verdict_ok = (bool(verdict) and verdict["verdict"] == critic.APPROVE
                  and (critic.is_independent(verdict) or critic.is_pre_gate(verdict)))
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
            critiqued = (bool(critic.evidence_for(root, rid))
                         and critic.is_independent_signoff(root, rid, signoff))
    return verified, reconciled, critiqued, doc_ok


def detect_conformance(repo_root: Path | str) -> dict:
    """Per-story lifecycle conformance.

    Returns {"units": [{id, type, status, stages, conformant, missing}],
    "summary": {total, conformant, nonconformant}}. A story is conformant when
    every required stage for its status is present.
    """
    root = Path(repo_root)
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
    units: list[dict] = []
    ok = 0
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        decomposed = sdlc_md.extract_field(text, "Epic") is not None
        has_ac, has_verify, verified_states = _ac_signals(text)
        verified = reconciled = critiqued = documented = promoted = None
        if status == "Done":
            verified, reconciled, critiqued, documented = _done_stages(
                root, rid, verified_states, _no_index, drift_ids, _doc_ok,
                two_role_cutoff=two_role_cutoff, critic_required=critic_required)
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
        rid_num = sdlc_md.id_number(rid)
        exempt = cutoff_num is not None and rid_num is not None and rid_num <= cutoff_num
        missing = [] if exempt else [s for s in required if not stages[s]]
        conformant = not missing
        ok += int(conformant and not exempt)
        units.append({
            "id": rid,
            "type": "story",
            "status": status,
            "stages": stages,
            "exempt": exempt,
            "conformant": conformant,
            "missing": missing,
            "downgraded": dod_downgrades if status == "Done" else [],
        })
    units.sort(key=lambda u: u["id"])
    total = len(units)
    exempt_n = sum(1 for u in units if u["exempt"])
    nonconformant = sum(1 for u in units if not u["conformant"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "summary": {"total": total, "conformant": ok,
                    "nonconformant": nonconformant, "exempt": exempt_n},
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
    judged = s["total"] - s.get("exempt", 0)
    tally: dict[str, int] = {}
    for u in result["units"]:
        if not u["conformant"]:
            for m in u["missing"]:
                tally[m] = tally.get(m, 0) + 1
    return sorted(k for k, c in tally.items() if judged >= 3 and c >= 0.8 * judged)


def remedy_detail(result: dict) -> str:
    """Gate-facing one-liner for a conformance failure: the bare count PLUS the two remedies
    (the adopt_after cutoff and the verify_ac backfill), and whether the shape reads as
    pre-existing unadopted-discipline debt (forward-only) rather than a fresh regression.
    Returns just the count when nothing is non-conformant."""
    n = result["summary"]["nonconformant"]
    if not n:
        return f"{n} non-conformant unit(s)"
    bulk = _bulk_missed(result)
    if bulk:
        nature = (f"most miss {', '.join(bulk)} - likely unadopted-discipline debt "
                  "(pre-existing, forward-only), not a regression from this change")
    else:
        nature = "scattered per-unit gaps - check whether this change regressed them"
    return f"{n} non-conformant unit(s): {nature}. Remedies: {REMEDY_CUTOFF}; or {REMEDY_BACKFILL}"


def cmd_check(args: argparse.Namespace) -> int:
    """Run the conformance check; exit non-zero if any unit is non-conformant."""
    result = detect_conformance(args.root)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        extra = f", {s['exempt']} exempt (pre-adoption)" if s.get("exempt") else ""
        print(f"conformance: {s['conformant']}/{s['total']} conformant, {s['nonconformant']} not{extra}"
              " (story-scoped: a bug/CR tranche relies on the critic + gate)")
        downgrades = next((u["downgraded"] for u in result["units"]
                           if u.get("downgraded")), [])
        if downgrades:
            print(f"  downgraded to human-judged by definition-of-done.md (tag removed): "
                  f"{', '.join(downgrades)}")
        tally: dict[str, int] = {}
        for u in result["units"]:
            if not u["conformant"]:
                print(f"  {u['id']} ({u['status']}): missing {', '.join(u['missing'])}")
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
    return 1 if result["summary"]["nonconformant"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio lifecycle-conformance check.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Check each story passed the required lifecycle stages.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
