# US0300: A stop names what could have proceeded, so the cost of stopping is visible

> **Status:** Done
> **Delivers:** CR0378
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0099
> **Points:** 2

## User Story

**As a** sprint operator reading a run afterwards
**I want** every stop to record why it stopped, which units its cause blocked, and which could
have carried on
**So that** a parked run can be told from a finished one and the price of parking it is on the
record rather than inferred

## Acceptance Criteria

### AC1: the stop record carries its cause and the units the cause blocked

- **Given** a run that stops
- **When** the stop is recorded
- **Then** the run state carries the cause, the units that cause blocked, and the time of the
  stop, so a parked run reads differently from a finished one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_stop_records_its_cause_and_the_units_it_blocked
- **Verified:** yes (2026-07-22)

### AC2: a forced stop names what could have proceeded

- **Given** an operator stop taken while units remain that no pending question blocks
- **When** the stop is recorded and reported
- **Then** those units are named individually as the cost of the stop, rather than folded into a
  count of remaining work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_forced_stop_names_the_units_that_could_have_proceeded
- **Verified:** yes (2026-07-22)

### AC3: the idle gap is marked and excluded from elapsed

- **Given** a stop record covering an interval the run spent waiting for an operator answer
- **When** the elapsed wall-clock for the run is reported
- **Then** the idle interval is marked and excluded, so points per elapsed-hour is never
  computed over a period the run spent waiting rather than working
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_elapsed_marks_and_excludes_the_recorded_idle_gap
- **Verified:** yes (2026-07-22)

### AC4: only idle the run's own window contained is ever deducted

- **Given** a wait recorded by the REAL `sprint stop` flow, which opens the gap at the instant
  the run closes, so the wait lies wholly outside the measured window
- **When** the elapsed wall-clock is reported
- **Then** the deduction removes nothing, the run reports the hours it actually worked, and the
  wait is still reported in full as recorded idle rather than discarded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k "test_a_wait_that_begins_when_the_run_stops_deducts_nothing or test_only_the_part_of_a_wait_inside_the_run_is_deducted"
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0378 says the elapsed a run reports must mark any idle gap, but not where the deduction
  belongs: the run-state elapsed, `retro._elapsed_hours`, or the sprint report's velocity line.
  AC3 is written against the reported figure; the implementation picks the seam and the Verify
  line follows it - Owner: implementer
- [ ] Whether an excluded idle gap is also shown as its own figure (waited N minutes) or only
  removed from the denominator is unstated. Showing it keeps the stop's cost visible, which is
  this story's stated purpose - Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and ACs authored against CR0378 |
| 2026-07-22 | claude | Repair round 1 - AC3's verifier hand-wrote a gap INSIDE the run window, a shape the system cannot produce: `cmd_stop` opens the gap immediately before `close_run`, so it always begins at `ended_at` and closes afterwards, and the deduction removed time the wall clock never held (2h worked plus a 3h wait reported 0.0h). The deduction is now clamped to each gap's intersection with the run, AC4 added, and the property is driven through the real `sprint stop` CLI |
