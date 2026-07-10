# CR-0228: rerun the benchmark suite on the v4 release candidate

> **Status:** In Progress
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator directive (2026-07-10): rerun the benchmarks before v4 launches - the published figures (N=5, 2026-07-08) were measured against the pre-v4 skill, and the white paper (CR0227) should cite figures measured on what actually ships. Rerun protocol v2 (three arms, held-back suites, pre-registered) against the v4 RC skill payload; publish the dated report whichever way the results point; note explicitly if the v4 team-generation and consult-quota changes alter any arm's behaviour. A faithful N=5 re-measure beats an unfinished N=10.

## Acceptance Criteria

- [ ] Protocol v2 rerun against the v4 RC payload (same three arms, same fixtures, same held-back suites); the run is dated and its report published in docs/benchmarks/ regardless of direction
- [ ] Every benchmark figure cited in docs/why-sdlc-studio.md, README.md, and the white paper is re-checked against the fresh report and updated (or explicitly kept with the measurement date named) - no stale number ships uncaptioned
- [ ] Any behaviour change attributable to v4 features (generated team, consult quota, plan-review gate) in any arm is named in the report's findings, flattering or not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
