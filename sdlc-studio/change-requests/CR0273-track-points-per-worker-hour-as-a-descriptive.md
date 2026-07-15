# CR-0273: Track points-per-worker-hour as a descriptive velocity metric, runner-only, never a target

> **Status:** Proposed
> **Priority:** P2
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The estimator measures tokens-per-point (cost); it does not track WALL-CLOCK throughput. Add a points-per-worker-hour figure - a human-legible planning read ('a runner sprint of N points takes about H hours of worker time') - derived from the run-state timestamps and the per-unit worker time the runner already measures. It complements tokens-per-point on a different axis: cost vs throughput.

## Impact

Belongs in the estimator/velocity workstream (RFC0038 lineage). TWO hard constraints, both learned from the token estimator: (1) RUNNER-ONLY. An interactively-driven sprint's wall-clock is confounded by human typing, agent thinking and background review round-trips - it is the session's conversational PACE, not the tool's throughput - exactly why this session's token cost is UNMEASURED. So points-per-worker-hour is measured ONLY from autosprint runner sprints (worker time, no human-in-loop latency); an interactive sprint is reported UNMEASURED, never counted. (2) DESCRIPTIVE, NEVER A TARGET. A tracked velocity becomes a target, and a velocity target corrupts point honesty (Goodhart) - the very thing this project guards with relative sizing, refuse-above-8, decomposition and record-never-auto-refit. So it goes in the retro accuracy block + VELOCITY.md as a trend a human reads, and is kept OUT of the capacity/appetite planning inputs (which already use wall-clock only as a breaker CEILING, not a throughput estimate). Who this affects: the operator gets an honest 'how long does a runner sprint take' number without a metric that can be gamed.

## Acceptance Criteria

- [ ] The retro accuracy block and VELOCITY.md carry a points-per-worker-hour figure derived from run-state timestamps + measured per-unit worker time, for a runner-driven sprint
- [ ] An interactively-driven sprint (no runner worker-time record) is reported UNMEASURED for wall-clock velocity, never counted - the same discipline as the token cost
- [ ] The figure is descriptive only: it does NOT feed capacity.minutes / appetite or any planning gate, and nothing is auto-refitted from it
- [ ] A test pins that an interactive sprint reads UNMEASURED and a runner sprint computes the figure from its worker-time records

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
