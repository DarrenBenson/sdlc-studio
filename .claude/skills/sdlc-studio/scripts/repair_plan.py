#!/usr/bin/env python3
"""The repair-plan gate (EP0106 / RFC0053).

The repair is the only step in the delivery loop with no review before execution. A story's
implementation plan is gated by `plan_review.py`; the code is reviewed after it is written;
and the repair between them has neither. It is also where defects are manufactured: over one
sprint every round from three to ten found a defect created by the previous round's repair,
and in each case the flaw was in the APPROACH and would have been visible in a written plan.

This module makes the repair a planned, reviewed step. A REJECT produces a written plan - one
entry per finding, naming the change, the approach and what it might break. The plan is put to
an independent pass BEFORE any code is written, briefed with the questions this loop keeps
failing. The verdict is pinned to the findings it answered, so a later finding invalidates it.
And a repair records which plan it executed, so a planned repair is distinguishable from one
that was not.

The gate is opt-in per project and OFF by default (US0315): an existing project's close does
not change until it sets `review.repair_plan_gate: on`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402
import critic  # noqa: E402

#: The config key that turns the gate on. Named ONCE, here, so the string the documentation
#: quotes and the string the code reads are the same object - BG0250 shipped a key four
#: documents said was read that no code read, and a hand-copied constant reproduces it. A test
#: takes this name from the documented spelling rather than restating it.
GATE_KEY = "review.repair_plan_gate"

#: The four questions this loop kept failing, in the brief for a repair-plan review. Each is a
#: question a previous round answered wrongly by not asking it. Held as data so a test can
#: assert the brief carries every one, and a brief missing any is refused rather than issued.
FOUR_QUESTIONS = (
    "Does the fix introduce the class it repairs?",
    "Is it a restatement of a rule that lives in code elsewhere, and could it be DERIVED?",
    "What did the previous attempt believe that turned out to be false?",
    "What does this change make it harder to notice?",
)

#: The fifth question, added for a repeat-class repair (US0344): not only is this fix correct,
#: but has the approach failed often enough that the APPROACH is the defect.
APPROACH_QUESTION = ("Has this approach failed enough rounds that the approach itself is the "
                     "defect, rather than this instance of it?")

_DESIGN = ("retain", "change")


def _plans_dir(root: Path | str) -> Path:
    return Path(root) / "sdlc-studio" / ".local" / "repair-plans"


def _plan_path(root: Path | str, plan_id: str) -> Path:
    return _plans_dir(root) / f"{plan_id}.json"


def findings_fingerprint(findings) -> str:
    """A hash of the finding SET this plan answers, order- and whitespace-independent.

    Following `plan_review.ac_fingerprint`, which pins a story plan to its ACs. Sorting and
    collapsing whitespace is deliberate: a verdict must survive the same findings re-read in a
    different order (US0313 AC3), and must NOT survive a finding added or removed (AC2).
    """
    norm = sorted(" ".join(str(f).split()) for f in findings)
    return hashlib.sha256("\x00".join(norm).encode("utf-8")).hexdigest()[:16]


def _finding_class(finding: str) -> str:
    """The CLASS of a finding, for detecting a repeat across rounds. A leading `class:` tag
    names it explicitly; otherwise the finding's own text is its class, so an identical
    finding recurring is a repeat and a reworded one is not (the conservative direction - a
    missed repeat under-fires the design-decision gate, which is recoverable)."""
    m = re.match(r"\s*class:\s*(\S+)", str(finding))
    return m.group(1) if m else " ".join(str(finding).split())


def gate_enabled(root: Path | str) -> bool:
    """Is the repair-plan gate on for this project? OFF unless explicitly set (US0315 AC1)."""
    try:
        val = config.get(root, GATE_KEY, "off")
    except Exception:  # noqa: BLE001 - config must never break the gate
        val = "off"
    return str(val).strip().lower() in ("on", "true", "yes", "1", "required")


def build_brief(prior_findings=None) -> dict:
    """The reviewer brief for a repair-plan review. Carries the four questions this loop keeps
    failing; for a repeat-class repair it also carries the approach question and an enumeration
    of what the class has already tried (US0344), because a reviewer asked whether an approach
    is exhausted cannot answer from the current plan alone."""
    questions = list(FOUR_QUESTIONS)
    prior = list(prior_findings or [])
    if prior:
        questions.append(APPROACH_QUESTION)
    return {"questions": questions, "prior_approaches": prior}


def validate_brief(brief: dict) -> None:
    """Refuse a brief missing any of the four questions (US0312 AC3), or - when it covers a
    repeat class - the approach question and the prior-approach enumeration (US0344)."""
    qs = list(brief.get("questions") or [])
    missing = [q for q in FOUR_QUESTIONS if q not in qs]
    if missing:
        raise ValueError(
            "repair-plan brief is missing question(s) this loop keeps failing: "
            + "; ".join(missing) + " - a brief that omits a question cannot ask it")
    if brief.get("prior_approaches"):
        if APPROACH_QUESTION not in qs:
            raise ValueError(
                "a repeat-class brief must ask whether the APPROACH is the defect, not only "
                "whether this fix is correct (US0344) - it is missing the approach question")


def repeat_rounds(root: Path | str, finding_class: str) -> int:
    """How many prior recorded repair plans already answered a finding of this class. The
    evidence behind the design-decision gate (US0343): two consecutive failures of one
    approach can be bad luck; more is a signal about the design."""
    d = _plans_dir(root)
    if not d.is_dir():
        return 0
    n = 0
    for f in sorted(d.glob("*.json")):
        try:
            plan = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        classes = {_finding_class(e.get("finding", "")) for e in plan.get("entries", [])}
        if finding_class in classes:
            n += 1
    return n


def design_threshold(root: Path | str) -> dict:
    """The number of failed rounds at which a repeat-class repair must change the design
    rather than propose another instance. Configurable; the default carries the evidence it
    rests on rather than being a bare number somebody chose (US0343 AC2)."""
    default = 2
    try:
        val = int(config.get(root, "review.repair_design_threshold", default))
    except Exception:  # noqa: BLE001
        val = default
    return {"value": val,
            "basis": ("default 2: over RUN-01KY5EJX one guard's approach class - enumerating "
                      "what a runner reads - failed FOUR consecutive rounds before it was "
                      "abandoned, and each round manufactured the next round's defect; two is "
                      "the point past which a third instance is more likely churn than fix")}


def record_repair_plan(root: Path | str, plan_id: str, verdict: str, findings,
                       entries, author: str) -> Path:
    """Write a repair plan: one entry per finding, each naming the change, the approach and
    what it might break. Refuses before writing anything (all-validate-then-write) when:

    - the verdict is not REJECT (US0311 AC3): a plan cannot be manufactured to launder a change
      nobody rejected;
    - an entry names no approach or no risk (US0311 AC2): an entry without an approach is a
      restatement of the finding, and one without a risk asserts the repair is free;
    - the plan has fewer entries than the verdict has findings, or an entry answers no listed
      finding (US0311 AC1): a silently unanswered finding is how a round's defects survive;
    - a repeat-class entry does not declare the design retained or changed, or - past the
      threshold - declares it retained while proposing only another instance (US0343).
    """
    root = Path(root)
    if str(verdict).upper() != critic.REJECT:
        raise ValueError(
            f"a repair plan exists only for a REJECT; the verdict is {verdict!r}. A plan "
            "against a non-REJECT verdict would launder a change nobody rejected (US0311 AC3)")
    findings = [str(f) for f in findings]
    answered = [str(e.get("finding", "")) for e in entries]
    unanswered = [f for f in findings if f not in answered]
    if unanswered:
        raise ValueError(
            "repair plan is missing an entry for finding(s): " + "; ".join(unanswered)
            + " - a plan with fewer entries than the verdict has findings leaves a defect "
            "silently unanswered (US0311 AC1)")
    thr = design_threshold(root)
    for e in entries:
        fid = str(e.get("finding", ""))
        if fid not in findings:
            raise ValueError(
                f"repair-plan entry answers {fid!r}, which is not a finding of this verdict "
                f"- every entry must name a finding the verdict raised (US0311 AC1)")
        for field in ("change", "approach", "risk"):
            if not str(e.get(field, "")).strip():
                raise ValueError(
                    f"repair-plan entry for {fid!r} names no {field}. An entry without an "
                    f"approach is a restatement of the finding; without a risk it asserts the "
                    f"repair is free - the belief every failed round held (US0311 AC2)")
        prior = repeat_rounds(root, _finding_class(fid))
        if prior:
            design = str(e.get("design", "")).strip().lower()
            if design not in _DESIGN:
                raise ValueError(
                    f"finding {fid!r} is in a class answered {prior} prior round(s); its "
                    f"entry must declare the design RETAINED or CHANGED and why, not describe "
                    f"a better instance of the same approach (US0343). Set `design` to one of "
                    f"{_DESIGN}")
            if design == "retain" and prior >= thr["value"]:
                raise ValueError(
                    f"finding {fid!r} has failed {prior} round(s) (threshold {thr['value']}): "
                    f"a plan that RETAINS the design and proposes another instance is refused "
                    f"- {thr['basis']}. Change the approach, or record why retention is right "
                    f"in a way the reviewer must rule on")
    d = _plans_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    plan = {"plan_id": plan_id, "verdict": critic.REJECT, "author": author,
            "findings": findings, "fingerprint": findings_fingerprint(findings),
            "entries": entries, "created": sdlc_md.now_iso8601()}
    p = _plan_path(root, plan_id)
    p.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return p


def load_plan(root: Path | str, plan_id: str) -> dict | None:
    p = _plan_path(root, plan_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def review_repair_plan(root: Path | str, plan_id: str, verdict: str, reviewer: str,
                       author: str) -> Path:
    """Record an independent verdict on a repair plan, pinned to the findings it answered.

    Refuses self-approval (US0312 AC2): the reviewer identity must differ from the plan's
    author, on the same rule the story-plan gate applies, so independence is mechanical rather
    than a convention the author is asked to honour. The verdict carries the findings
    fingerprint (US0313 AC1), so a later finding invalidates it.
    """
    plan = load_plan(root, plan_id)
    if plan is None:
        raise FileNotFoundError(f"no repair plan {plan_id!r} to review")
    if _clean(reviewer) == _clean(plan.get("author", "")) or _clean(reviewer) == _clean(author):
        raise ValueError(
            f"a plan's author cannot record its own review ({reviewer!r}). The repair-plan "
            "review is an independent pass; a delegate the author controls does not satisfy "
            "it (US0312 AC2)")
    fp = plan.get("fingerprint", "")
    issues = f"plan={plan_id}; findings-hash={fp}"
    return critic.record_verdict(root, plan_id, verdict, reviewer, author, issues,
                                 phase="plan-review")


def _clean(s: str) -> str:
    return " ".join(str(s or "").split()).lower()


def plan_reviewed(root: Path | str, plan_id: str) -> dict:
    """Is this repair plan independently approved against its CURRENT findings? Returns
    {ok, reason}. A verdict pinned to a stale finding set does not count (US0313 AC2); the
    same findings re-read in a different order still count (US0313 AC3)."""
    plan = load_plan(root, plan_id)
    if plan is None:
        return {"ok": False, "reason": f"no repair plan {plan_id!r}"}
    v = critic.verdict_for(root, plan_id, phase="plan-review")
    if not v or v.get("verdict") != critic.APPROVE:
        return {"ok": False, "reason": "no independent APPROVE on this repair plan"}
    if not critic.is_independent(v):
        return {"ok": False, "reason": "the recorded plan verdict is not independent "
                                       "(reviewer == author)"}
    m = re.search(r"findings-hash=([0-9a-f]+)", v.get("issues", "") or "")
    current = findings_fingerprint(plan.get("findings", []))
    if not m:
        # DECIDED, not passed over: a verdict carrying no findings-hash is NOT pinned. It
        # answers no stated finding set, so nothing can show it answered THIS one, and a
        # check that accepts it is asserting an absence is a match. `review_repair_plan`
        # always writes the token, so this is the hand-edited or directly-recorded verdict -
        # precisely the case the pin exists for. Re-review the plan to re-pin it.
        return {"ok": False, "reason": ("the plan verdict carries no findings-hash, so nothing "
                                        "pins it to the findings it answered - re-review the "
                                        "plan with `review_repair_plan` to pin it")}
    if m.group(1) != current:
        return {"ok": False, "reason": ("the plan verdict answered a different finding set; a "
                                        "finding added or removed since invalidates it "
                                        "(US0313 AC2)")}
    return {"ok": True, "reason": "independent APPROVE pinned to the current findings"}


def repair_gate(root: Path | str, plan_id: str | None, repaired_at=None,
                plan_reviewed_at=None) -> dict:
    """The gate: may a repair be recorded? Returns {ok, reason}.

    OFF unless `review.repair_plan_gate` is set, so an upgrading project's close does not
    change (US0315 AC1). When ON, a repair with no reviewed plan is refused (US0312 AC1), and
    a plan verdict recorded AFTER the repair commit does not satisfy it (US0312 AC4): a review
    that followed the work is a description of it, not an attack on it.
    """
    if not gate_enabled(root):
        return {"ok": True, "reason": f"repair-plan gate off (set `{GATE_KEY}: on` to enable)"}
    if not plan_id:
        raise ValueError(
            f"the repair-plan gate is on (`{GATE_KEY}`), so a repair must name the plan it "
            "executed. This repair names none - write and review a plan first (US0312 AC1)")
    rev = plan_reviewed(root, plan_id)
    if not rev["ok"]:
        raise ValueError(f"repair refused: {rev['reason']} ({GATE_KEY} is on)")
    if repaired_at is not None and plan_reviewed_at is not None and plan_reviewed_at > repaired_at:
        raise ValueError(
            "the plan review was recorded AFTER the repair it authorises. A review that "
            "followed the work describes it rather than attacking it, and does not satisfy "
            "the gate (US0312 AC4)")
    return {"ok": True, "reason": "reviewed repair plan on record"}


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------
def _cmd_brief(args) -> int:
    brief = build_brief(args.prior or [])
    print(json.dumps(brief, indent=2))
    return 0


def _cmd_gate(args) -> int:
    try:
        res = repair_gate(args.root, args.plan)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(res["reason"])
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="The repair-plan gate (EP0106).")
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brief", help="print the reviewer brief for a repair-plan review")
    b.add_argument("--prior", nargs="*", help="prior approaches this class has already tried")
    b.set_defaults(func=_cmd_brief)
    g = sub.add_parser("gate", help="check whether a repair may be recorded")
    g.add_argument("--plan", help="the repair plan id the repair executed")
    g.set_defaults(func=_cmd_gate)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
