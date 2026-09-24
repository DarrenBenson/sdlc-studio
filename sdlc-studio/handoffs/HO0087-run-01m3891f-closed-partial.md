# HO-0087: RUN-01M3891F closed partial

> **Date:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M3891F (started 2026-09-23T23:32:40Z)
> **Outcome:** running
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Unanswered stop-ship questions

None: every batch unit is delivered, abandoned, ruled, dropped, parked or awaiting only a signature. Rulings read from RETRO0122's `## Known issues carried` for RUN-01M3891F.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 297.2 min, 11 unit(s) terminal
- **Delivered:** 11 unit(s)
- **Token forecast:** ~14,860,020 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (11)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [US0879](../../sdlc-studio/stories/US0879-a-commit-runs-only-the-checks-that-catch.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa-rev-US0879) |
| [US0880](../../sdlc-studio/stories/US0880-a-commit-s-tests-finish-inside-a-90.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa-rev-US0880) |
| [US0881](../../sdlc-studio/stories/US0881-a-push-runs-the-full-suite-once-and.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa-rev-US0881) |
| [US0882](../../sdlc-studio/stories/US0882-mutation-evidence-that-is-switched-off-stops-blocking.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa-rev-US0882) |
| [US0883](../../sdlc-studio/stories/US0883-a-signed-report-cannot-be-edited-unnoticed.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa-rev-US0883) |
| [US0884](../../sdlc-studio/stories/US0884-a-sprint-report-is-filed-only-by-the.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (qa-rev-US0884) |
| [US0885](../../sdlc-studio/stories/US0885-a-report-s-time-window-does-not-race.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (qa-rev-US0885) |
| [US0886](../../sdlc-studio/stories/US0886-criteria-that-sprint-1-superseded-are-retired-not.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (qa-rev-US0886) |
| [US0887](../../sdlc-studio/stories/US0887-a-lesson-is-a-failure-class-that-counts.md) | story | Done | 3/3 AC(s) verified; critic APPROVE (qa-rev-US0887) |
| [US0888](../../sdlc-studio/stories/US0888-a-lesson-that-recurs-graduates-into-a-check.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa-rev-US0888) |
| [US0889](../../sdlc-studio/stories/US0889-the-close-forward-ports-the-skill-and-keeps.md) | story | Done | 2/2 AC(s) verified; critic APPROVE (qa-rev-US0889) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Generated at the run close (`handoff generate`) |
