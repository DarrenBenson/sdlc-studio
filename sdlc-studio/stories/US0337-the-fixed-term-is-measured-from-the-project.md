# US0337: The fixed term is MEASURED from the project's own velocity record, and reads UNMEASURED rather than a default where fewer than two sprints carry a whole-sprint actual

> **Status:** Done
> **Delivers:** CR0391
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py,.claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0114
> **Points:** 3
> **Depends on:** BG0257

## User Story

**As an** operator whose plan quotes a fixed per-sprint cost
**I want** that figure fitted from this project's own whole-sprint actuals, and reported as
UNMEASURED where too few sprints carry one
**So that** a constant nobody measured never enters the forecast wearing the authority of a
measurement

## Context

The fit reads the velocity record's Points and Actual columns. BG0257 is the write path into
those columns and it currently publishes a partially-parsed batch: a Points denominator over
four units where the sprint delivered thirty-three. Fitting a fixed term against a record that
can hold such a row would inherit the error and call it evidence, which is why BG0257 lands
first. That ordering is a constraint on the DATA this story reads, not on the files it edits.

## Acceptance Criteria

### AC1: the fixed term is fitted from the record's whole-sprint rows, which it names

- **Given** a velocity record carrying two or more out-of-sample rows with recorded Points and
  an Actual that covers the whole sprint
- **When** the fixed term is measured
- **Then** it is fitted from exactly those rows and the answer names the retro ids it rests
  on, so the figure is traceable to the rows that produced it rather than being asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheFixedTermIsMeasuredFromTheRecordTests::test_the_fit_uses_the_whole_sprint_rows_and_names_them
- **Verified:** yes (2026-07-23)

### AC2: fewer than two qualifying sprints reads UNMEASURED and supplies no figure

- **Given** a record with one qualifying row, or none
- **When** the fixed term is asked for
- **Then** the answer is UNMEASURED and carries no number at all - not the shipped seed, not
  zero, not a scaled default - and states how many qualifying sprints it found
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheFixedTermIsMeasuredFromTheRecordTests::test_fewer_than_two_qualifying_rows_reads_unmeasured_and_supplies_no_figure
- **Verified:** yes (2026-07-23)

### AC3: a per-unit build sum does not count toward the two

- **Given** a record whose two rows are one sprint-level total and one per-unit build sum
  (Measured equals Units)
- **When** the fixed term is asked for
- **Then** only one row qualifies, the answer is UNMEASURED, and the excluded row is named
  with the reason: a build sum omits the ceremony the fixed term exists to price, so counting
  it would fit the fixed cost against data that never contained it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::TheFixedTermIsMeasuredFromTheRecordTests::test_a_per_unit_build_sum_row_does_not_count_toward_the_two
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
