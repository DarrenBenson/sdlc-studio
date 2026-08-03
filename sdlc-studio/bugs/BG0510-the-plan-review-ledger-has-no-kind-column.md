# BG0510: the plan-review ledger has no kind column, so a second pre-code gate would be cleared by the first gate's approval

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Found at the plan-time goal review for RUN-01KZ (EP0207), independently by the QA and product seats, each by reading critic.py and plan_review.py rather than by running the batch. Confirmed by the author at transition.py's plan_review.gate call site and at critic.verdict_for.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A plan-review verdict is keyed by unit and phase only - `critic.verdict_for(root, unit, phase='plan-review')` returns the latest row for that pair, and `plan-review-verdicts.md` carries no column saying WHAT was reviewed. Today only one kind of plan review exists: the US0090 pre-implementation AC-vs-spec check that `plan_review.gate` enforces from `transition.py` on entry to In Progress, Review or Done. That is sound while the kind is unique. It stops being sound the moment a second pre-code artefact is reviewed through the same phase, because one approval then discharges both gates and neither reviewer read the other's artefact. This was found while planning EP0207, whose US0630 proposed exactly that second gate: the criterion as drafted read 'an APPROVE row in plan-review-verdicts.md', which a design-plan approval satisfies with no test plan ever written. The criterion was withdrawn rather than shipped, so nothing in the tree is wrong today - what is wrong is that the ledger's shape makes the mistake the DEFAULT for the next author, and two independent review seats found it only by reading the source.

## Steps to Reproduce

1. Read `critic.verdict_for` - the signature is (`repo_root`, unit, phase) and the phase vocabulary is the two-item PHASES tuple.
2. Read the header of sdlc-studio/reviews/plan-review-verdicts.md - the row schema is Unit, Verdict, Reviewer, Author, Date, Issues. Nothing records which artefact was judged.
3. Read transition.py where it calls `plan_review.gate` - the one consumer, and the reason the ambiguity is currently harmless.

## Proposed Fix

Give a plan-review row a KIND (the artefact judged - spec, test-plan, whatever follows) and make the lookup take it. Default the existing rows to the spec kind so no history is reinterpreted. A gate then asks for an approval of the artefact it actually cares about, and a phase with one kind stays a one-word change away from a phase with two.

## Acceptance Criteria

- [ ] The behaviour described is corrected: A plan-review verdict is keyed by unit and phase only - `critic.verdict_for(root, unit, phase='plan-review')` returns the latest row for that pair, and...
- [ ] The proposed fix lands, pinned by a test: Give a plan-review row a KIND (the artefact judged - spec, test-plan, whatever follows) and make the lookup take it.

## Impact

Latent rather than live. It costs nothing today and it silently mis-designs the next pre-code gate somebody adds - which is a gate whose whole purpose is to refuse work, so the failure mode is a gate that passes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
