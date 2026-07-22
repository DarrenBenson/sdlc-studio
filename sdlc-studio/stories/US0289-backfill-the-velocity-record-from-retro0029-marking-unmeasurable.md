# US0289: Backfill the velocity record from RETRO0029, marking unmeasurable rows as such

> **Status:** Review
> **Delivers:** CR0284
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/retros/VELOCITY.md,.claude/skills/sdlc-studio/scripts/retro.py
> **Epic:** EP0094
> **Points:** 3

## User Story

**As an** operator reading the velocity record to decide what a sprint will cost
**I want** every retro since RETRO0028 to have a row, blank and reasoned where nothing was
measured
**So that** a gap in the record is a statement about a sprint rather than an absence I cannot
tell from an oversight

## Context

`sdlc-studio/retros/` holds 65 retros. `VELOCITY.md` holds 18 rows, and the window CR0284 names
(RETRO0029 onwards) is missing roughly half of them - RETRO0029 to RETRO0043, RETRO0046,
RETRO0047, RETRO0051 to RETRO0056 and RETRO0059 have no row at all.

Nothing detects that. `velocity_history` reads the rows that exist and `cmd_velocity` prints
them; a retro that never reached the file is invisible to both, so the record can rot without
any command saying so. The backfill is worth nothing on its own: without a gap reporter the same
hole reopens the next time a close skips the write.

The file's own header already fixes what a blank row means. An empty Actual is never 0, and the
Note column says why it is empty. That vocabulary exists in `_actual_note`; this story uses it
rather than inventing a second one, and it must not manufacture what the header forbids - a row
re-derived from today's constants is not a record of a prediction.

## Acceptance Criteria

### AC1: a gap in the record is reported

- **Given** a retro on disk with no row in `VELOCITY.md`
- **When** the velocity reader runs its gap report
- **Then** it names that retro and exits non-zero, so a skipped accuracy write is visible instead
  of being indistinguishable from a sprint that never happened
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py -k test_velocity_gaps_names_every_retro_with_no_row
- **Verified:** yes (2026-07-22)

### AC2: this repo's record has no gap from RETRO0029 onwards

- **Given** this repo's own retros and `VELOCITY.md`
- **When** the gap report runs bounded at RETRO0029
- **Then** it reports none, because every retro in the window carries a row
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/retro.py velocity --gaps --since RETRO0029
- **Verified:** yes (2026-07-22)

### AC3: an unrecoverable total is a blank Actual with a recorded reason, never a zero

- **Given** a sprint whose token cost cannot be recovered
- **When** its row is written
- **Then** the Actual cell is blank and the Note cell states why, and no row in the window
  carries a `0` Actual, because a sum over an empty set of measured units is not a measurement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py -k test_an_unrecoverable_total_is_a_blank_actual_with_a_reason
- **Verified:** yes (2026-07-22)

### AC4: a backfilled row claims no forecast it never made

- **Given** a sprint that recorded no plan-time forecast
- **When** its row is backfilled
- **Then** the Estimate cell is empty and the Sample cell reads unforecast, rather than being
  re-derived from the constants in force today, which would make the row read as a prediction
  nobody made
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py -k test_a_backfilled_row_records_no_forecast_it_never_made
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0284 asks for rows "where totals are recoverable" without saying from what. Harness
  capture is session-cumulative and several closed runs predate the baseline it needs, so which
  historical totals are genuinely recoverable is a per-retro judgement made at delivery; a row is
  written either way, and AC3 governs the ones that are not - Owner: operator
- [ ] Retros before RETRO0029 are out of scope here. Whether the window should later extend back
  to RETRO0001 or be declared closed is not decided - Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed against CR0284 AC2 and the VELOCITY.md header's rules for a blank cell |
