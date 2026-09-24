# EP0248: A change to a gate lane or a hook is run where the hook runs it before it can reach Fixed

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Derived Point Total:** 18
> **Parent:** CR0565
> **Created:** 2026-09-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** S

## Summary

Decomposed from CR0565. Delivers the work CR0565 requested.

## Story Breakdown

- [x] [US0817: A unit whose Affects names a gate lane, a hook or the suite runner cannot reach Fixed or Done without a recorded green self-run of the affected lane on this repository](../stories/US0817-a-unit-whose-affects-names-a-gate-lane.md)
- [x] [US0855: the self-run WRITER: a recording command upserts a Self-run field carrying lane, verdict, wall clock and a hash over the unit's gate-surface bytes](../stories/US0855-the-self-run-writer-a-recording-command-upserts.md)
- [x] [US0856: the self-run GATE: a unit whose Affects names the derived gate surface cannot reach Fixed or Done without a green, current self-run](../stories/US0856-the-self-run-gate-a-unit-whose-affects.md)
- [x] [US0857: the pre-push hook runs its own gate against HEAD under SDLC_PRE_PUSH_SELF_RUN and pushes nothing, so a hook change can record a self-run](../stories/US0857-the-pre-push-hook-runs-its-own-gate.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - self-run gate for gate/hook changes: US0881's full suite at push runs hooks as the hook does |
