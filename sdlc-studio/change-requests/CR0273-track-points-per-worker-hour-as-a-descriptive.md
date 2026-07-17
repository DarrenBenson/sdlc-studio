# CR-0273: Track sprint velocity (points per elapsed sprint), ceremony included, as a descriptive planning metric

> **Status:** Superseded
> **Superseded-by:** RFC0035
> **Priority:** P2
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The estimator measures tokens-per-point (cost); it does not track VELOCITY - points delivered per sprint. Add a **points-per-sprint / points-per-elapsed-hour** figure as the PRIMARY, human-legible planning read ("a session delivers about N points"; "a sprint of N points takes about H hours"), derived from the run-state start and close timestamps. Ceremony is INCLUDED by design - planning, review, retro and verification are part of the sprint, not overhead to strip out - exactly as real Scrum velocity is points-per-timebox, never coding time. A SECONDARY points-per-WORKER-hour (the runner's worker time, ceremony removed) is reported to tune the tool, but it is explicitly NOT the planning number.

## Impact

Belongs in the estimator/velocity workstream (RFC0038 lineage). The reframe (from an earlier draft that made worker-time the primary): the number an operator plans around is the END-TO-END one - points per elapsed sprint, ceremony and all - because that is what predicts what a session delivers. Stripping the ceremony measured the tool, not the delivery.

FOUR constraints:

1. PRIMARY = ELAPSED, CEREMONY INCLUDED. Points delivered / elapsed sprint time (run-state open -> close). Planning, review round-trips, retro and the verification/suite runs are counted - they ARE the sprint.
2. FIXED CEREMONY COST -> IT IS "POINTS PER SESSION". The ceremony floor (one review pass, a couple of suite runs, one retro) is roughly fixed per sprint, not per point. So the figure holds for similar-sized single-session sprints (the ~5-20 point envelope observed) and must NOT be read as a linear per-point rate to extrapolate to a 1-point or a 100-point sprint - the same way a team's velocity predicts the next sprint but not a half-day or a month.
3. SECONDARY = WORKER TIME (runner only). Points per runner worker-hour, ceremony removed, for tuning the tool. Clearly labelled distinct from the planning velocity. An interactive sprint has no clean worker-time, so this secondary reads UNMEASURED there.
4. DESCRIPTIVE, NEVER A TARGET. A tracked velocity becomes a target, and a velocity target corrupts point honesty (Goodhart) - the very thing this project guards with relative sizing, refuse-above-8, decomposition and record-never-auto-refit. Both figures go in the retro + VELOCITY.md as a trend a human reads, and are kept OUT of capacity/appetite and any planning gate (capacity already uses wall-clock only as a breaker CEILING, not a throughput estimate).

Honesty note on elapsed time: the runner gives a clean elapsed (open -> close, no external gaps). An interactively-driven sprint's elapsed time includes stretches where the operator is away, so the PRIMARY figure for an interactive sprint is either flagged with that caveat or reported UNMEASURED - the number must not silently count idle time as sprint time.

## Acceptance Criteria

- [ ] The retro accuracy block and VELOCITY.md carry a PRIMARY points-per-sprint velocity (points delivered / elapsed sprint hours from the run-state open->close timestamps), with ceremony included, matching how Scrum velocity is defined
- [ ] A SECONDARY points-per-worker-hour (runner worker time, ceremony removed) is reported for tool tuning, clearly labelled as distinct from the planning velocity, and reads UNMEASURED for an interactive sprint
- [ ] The primary figure is labelled "points per session/sprint" and carries the fixed-ceremony caveat (holds within the single-session envelope; not a linear per-point rate); an interactive sprint whose elapsed time is confounded by operator-away gaps is flagged or UNMEASURED, never counted as clean
- [ ] Both figures are DESCRIPTIVE only: neither feeds capacity.minutes / appetite or any planning gate, and nothing is auto-refitted from either
- [ ] A test pins the elapsed-velocity computation from run-state timestamps and the descriptive-only guarantee (no capacity/gate coupling)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
| 2026-07-15 | sdlc-studio | Reframed: the PRIMARY metric is points-per-elapsed-sprint (ceremony INCLUDED), the operator's planning number; points-per-worker-hour demoted to a secondary tool-tuning figure. Ceremony is the sprint, not overhead - real Scrum velocity is points-per-timebox. |
| 2026-07-16 | sdlc-studio | Superseded by RFC0035 (the sprint-report workstream), which absorbs these five acceptance criteria; recorded the Superseded-by pointer so the trace can follow where the work went. |
