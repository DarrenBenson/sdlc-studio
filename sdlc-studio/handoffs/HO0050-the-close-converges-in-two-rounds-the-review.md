# HO-0050: The close converges in two rounds, the review costs what the unit's risk deserves, and a run can be signed off without waiting for a human

> **Date:** 2026-08-06
> **Created-by:** sdlc-studio new
> **Run:** RUN-01KZ9315 (started 2026-08-05T14:01:38Z)
> **Outcome:** goal-reached
> **Goal:** done
> **Batch source:** argument

## Where to pick up

Every unit in the batch is terminal. There is no tail: close the run and plan the next batch normally.

## Appetite

- **Declared:** wall-clock 960 min, units 64 unit(s)
- **Spent:** 1223 min, 12 unit(s) terminal
- **Delivered:** 12 unit(s)
- **Token forecast:** ~3,164,819 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (12)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0495](../../sdlc-studio/bugs/BG0495-the-velocity-row-understates-twice-it-counts-only.md) | bug | Fixed | critic APPROVE (qa) |
| [BG0510](../../sdlc-studio/bugs/BG0510-the-plan-review-ledger-has-no-kind-column.md) | bug | Fixed | critic APPROVE (engineering) |
| [BG0520](../../sdlc-studio/bugs/BG0520-the-triage-session-cap-is-a-lifetime-cap.md) | bug | Fixed | critic APPROVE (engineering) |
| [BG0525](../../sdlc-studio/bugs/BG0525-us0629-ac2-asks-derive-to-detect-a-polarity.md) | bug | Fixed | critic APPROVE (engineering) |
| [US0638](../../sdlc-studio/stories/US0638-the-close-pre-flight-runs-the-retro-checklist.md) | story | Done | 6/6 AC(s) verified; critic APPROVE (engineering) |
| [US0639](../../sdlc-studio/stories/US0639-every-gate-execution-the-close-runs-is-recorded.md) | story | Done | 7/7 AC(s) verified; critic APPROVE (engineering) |
| [US0640](../../sdlc-studio/stories/US0640-plan-review-honours-its-own-enabled-key-rather.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (engineering) |
| [US0641](../../sdlc-studio/stories/US0641-the-critic-brief-tier-is-derived-from-the.md) | story | Done | 7/7 AC(s) verified; critic APPROVE (engineering) |
| [US0642](../../sdlc-studio/stories/US0642-a-low-band-unit-gets-a-bounded-brief.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (engineering) |
| [US0643](../../sdlc-studio/stories/US0643-a-seat-may-sign-only-work-it-neither.md) | story | Done | 7/7 AC(s) verified; critic APPROVE (engineering) |
| [US0644](../../sdlc-studio/stories/US0644-the-sign-off-record-states-that-a-seat.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (engineering) |
| [US0645](../../sdlc-studio/stories/US0645-the-operator-summary-is-derived-from-the-record.md) | story | Done | 4/4 AC(s) verified; critic APPROVE (qa) |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Generated at the run close (`handoff generate`) |
