# CR-0266: RFC0038 U2: sprint.py speaks points - the gate refuses above 8, WSJF is CoD/points, and the dead machinery is deleted

> **Status:** Complete
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Verification depth:** functional - attacked through the public CLI: a 13-point unit is refused (exit 2, no plan), the same batch at 8 plans (exit 0); a 2-point High outranks an 8-point Critical under --order wsjf and the reverse under --order priority; and `EFFORT_SIZE`, _effort_code, `BASE_TOKEN_BUDGET`, `TOKENS_PER_COGNITIVE`, `DEFAULT_UNKNOWN_SIZE` and the complexity tie-break all grep to zero (BG0147 closed).
> **Depends on:** CR0265
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

The core of RFC0038. sprint.py currently carries five overlapping size signals, three of them dead or unvalidated. This unit reduces it to one.

THE GATE REFUSES ABOVE 8 POINTS. This is not a ceremony bolted on - it is the rule that makes the model work, and the evidence demanded it. A point was a stable unit of cost from 2 to 8 (22k-27k tokens per point) and then broke: the 13s came in at 14,144 per point, systematically over-estimated, exactly where the literature says estimator consistency collapses. All three blind estimators returned both 13s with LOW confidence and the words "should be split", unprompted. The one sprint that failed the accuracy band contains a 13. Above 8, the estimate is not worth having, and the honest answer is to decompose - which is a triage decision, not an estimation one.

WSJF = CoD / Points, with Cost of Delay on the same Fibonacci scale, derived from Priority. No seat scores required, which is why the existing WSJF has almost never run.

FORECAST = sum(points) x measured tokens-per-point. The rate is measured from the evidence and re-measured each sprint, never fitted to a model.

DELETED: `EFFORT_SIZE`, `EFFORT_ALIAS`, `EFFORT_COMPLEXITY_PROXY`, `_effort_code`, `effort_points`, `BASE_TOKEN_BUDGET`, `TOKENS_PER_COGNITIVE`, and the `max_cognitive` WSJF tie-break (which closes BG0147 - a signal proven to score 0.03 against cost was still deciding the running order under a docstring vouching that "the smaller blast-radius job goes first").

Estimated at 8 points before the work: a real design decision, several machineries removed at once, and the forecast, the gate and the ordering all move together.

## Impact

Every sprint plan. It is the difference between a size number that means something and five that do not, and it makes the decomposition rule enforceable rather than advisory.

**Effort:** L

## Acceptance Criteria

- [ ] The grooming gate demands `Points` and REFUSES a unit above 8, naming it and saying why: above 8 the estimate is not worth having and the unit must be decomposed. The threshold is configurable, so a project that finds 8-point units too chunky can tighten it to 5.
- [ ] WSJF is Cost of Delay divided by Points, with CoD on the Fibonacci scale derived from Priority. It runs without seat scores.
- [ ] The token forecast is the sum of the points in the batch multiplied by a tokens-per-point rate MEASURED from the evidence, not fitted. The plan states the rate and the evidence it came from.
- [ ] `EFFORT_SIZE`, `EFFORT_ALIAS`, `EFFORT_COMPLEXITY_PROXY`, `_effort_code`, `effort_points`, `BASE_TOKEN_BUDGET` and `TOKENS_PER_COGNITIVE` are GONE from sprint.py, and the `max_cognitive` tie-break no longer orders the batch. A grep for them returns nothing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
