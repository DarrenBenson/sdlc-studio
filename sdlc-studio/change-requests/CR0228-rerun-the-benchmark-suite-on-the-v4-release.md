# CR-0228: rerun the benchmark suite on the v4 release candidate

> **Status:** Complete
> **Verification depth:** functional (72 oracle-scored runs, every reported figure recomputed independently by the critic from runs.jsonl + archived rubric/audit JSON; one REJECT round repaired; the white-paper clause of AC2 re-runs when CR0227 delivers)
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator directive (2026-07-10): rerun the benchmarks before v4 launches - the published figures (N=5, 2026-07-08) were measured against the pre-v4 skill, and the white paper (CR0227) should cite figures measured on what actually ships. Rerun protocol v2 (three arms, held-back suites, pre-registered) against the v4 RC skill payload; publish the dated report whichever way the results point; note explicitly if the v4 team-generation and consult-quota changes alter any arm's behaviour. A faithful N=5 re-measure beats an unfinished N=10.

## Acceptance Criteria

- [x] Protocol v2 rerun against the v4 RC payload (same three arms, same fixtures, same held-back suites); the run is dated and its report published in docs/benchmarks/ regardless of direction
- [x] Every benchmark figure cited in docs/why-sdlc-studio.md, README.md, and the white paper is re-checked against the fresh report and updated (or explicitly kept with the measurement date named) - no stale number ships uncaptioned
- [x] Any behaviour change attributable to v4 features (generated team, consult quota, plan-review gate) in any arm is named in the report's findings, flattering or not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-10 | Claude (sprint driver) | delivered: 72-run three-era rerun + post-hoc rubric axis (operator-requested); AC2's white-paper clause deferred to CR0227 close |
| 2026-07-10 | Claude (sprint driver) | exploratory mandated-arm addendum (operator claim test): Sonnet 5/5 -> 1/5 escapes at 1.18x when planning is mandatory; Sam verified every figure; calibration-phase rows keep measured aggregates clean |
