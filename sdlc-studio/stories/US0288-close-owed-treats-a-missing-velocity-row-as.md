# US0288: close_owed treats a missing velocity row as an owed close item

> **Status:** Done
> **Delivers:** CR0284
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py,.claude/skills/sdlc-studio/scripts/hooks/close_guard.py
> **Epic:** EP0094
> **Points:** 3

## User Story

**As an** operator closing a sprint
**I want** the close-owed detector to count a retro with no velocity row as an unfinished close
**So that** the accuracy write cannot be silently skipped and the estimator stays falsifiable

## Context

`close_owed.covered_ids` asks one question: does some retro's `Batch` name this unit? Nothing
anywhere in `close_owed.py` or `hooks/close_guard.py` asks whether the accuracy and velocity
write ran. That is the exact hole CR0284 records: `accuracy --tokens N --write` shipped, and
RETRO0039 onwards still closed with no row in `sdlc-studio/retros/VELOCITY.md`, so the rate the
plans quote has never been re-measured against them.

The demand is for the ROW, not for a token total. A row with a blank Actual and a recorded
reason is a complete close - it says the sprint's cost was not recoverable, which is a fact the
record holds. No row at all says nothing, and is indistinguishable from an oversight.

Scoped by the same grandfather doctrine the unit half already obeys: only a retro dated on or
after the baseline stamp can owe a row. Without that, adopting the check hands every project a
tail of historical retros no close can ever clear, which is the unclearable-debt failure the
baseline exists to prevent.

## Acceptance Criteria

### AC1: a retro with no velocity row is reported, and the detector exits non-zero

- **Given** a baselined project with a retro dated after the stamp and no row for it in
  `VELOCITY.md`
- **When** `close_owed detect` runs
- **Then** the report names that retro in its own field, distinct from the uncovered delivery
  units in `owed`, the render names it, and the command exits non-zero
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k "test_a_retro_with_no_velocity_row_is_owed or test_detect_exits_non_zero_on_a_missing_velocity_row"
- **Verified:** yes (2026-07-22)

### AC2: retros predating the baseline stamp are not demanded

- **Given** a project that stamps a baseline today with retros already on disk from before it
- **When** the detector runs
- **Then** none of those older retros is reported as owing a row, so adopting the check creates
  no debt that no close can clear
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k test_retros_before_the_baseline_stamp_owe_no_velocity_row
- **Verified:** yes (2026-07-22)

### AC3: a recorded override clears the demand and is reported, not hidden

- **Given** a retro carrying an explicit recorded override stating why it can have no velocity
  row
- **When** the detector runs
- **Then** that retro is not reported as owed, and the recorded reason appears in the report, so
  the escape is auditable rather than a silent pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py -k test_a_recorded_velocity_override_is_named_not_owed
- **Verified:** yes (2026-07-22)

### AC4: the Stop hook surfaces the missing row in its block reason

- **Given** a report carrying a retro that owes a velocity row and no uncovered delivery units
- **When** `close_guard.decide` runs on it
- **Then** it blocks once and its reason names the retro and the accuracy write that did not run,
  rather than reporting nothing because the unit half is clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_guard.py -k test_block_reason_names_a_retro_missing_its_velocity_row
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0284 asks for a flag "when a token total is supplyable" but does not define supplyable.
  This story demands the ROW and treats a row with a blank Actual plus a recorded reason as a
  complete close. Whether a present row whose Actual is blank while the harness COULD have been
  read should also be flagged is unresolved - Owner: operator
- [ ] CR0284 names a "recorded-override escape" without naming its form. AC3 assumes the override
  is recorded in the retro itself, so it travels with the record rather than in a command flag -
  Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0284 AC1, close_owed's baseline doctrine and the Stop hook |
