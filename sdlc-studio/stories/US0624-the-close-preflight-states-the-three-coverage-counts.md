# US0624: the close preflight states the three coverage counts separately

> **Status:** Done
> **Delivers:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0205
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator running the preflight before a close
**I want** approved, repaired and unreviewed counted separately on the coverage line
**So that** the one unit that genuinely needs a review is not hidden inside a crowd of false ones

## Notes

Delivers criterion 5 of CR0506, and it is where the whole epic becomes visible to the operator.
US0620 records the repair, US0621 computes the three states; without this they change a
predicate nobody reads.

The line being replaced said "28 of 44 unit(s) are covered by no independent review". It was
wrong by 18 out of 19, **and the reason it was wrong is that one number cannot carry three
states.** So the fix is not a better number - it is three.

This is a lane test, not a library test. The defect was never in the predicate's arithmetic; it
was in what the operator was shown, and only a check driving the shipped preflight can see that
(LL0040).

## Acceptance Criteria

### AC1: the preflight prints three counts, each named

- **Given** a batch containing approved, repaired and unreviewed units
- **When** `sprint.py preflight` runs
- **Then** its coverage line states the three counts separately with the states named, driven
  through the shipped command rather than through the predicate - the defect was in what the
  operator was shown
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightCoverageCountsTests::test_the_shipped_preflight_stops_calling_a_repaired_unit_uncovered
- **Verified:** yes (2026-08-03)

### AC2: the three counts sum to the batch, and the sum is asserted

- **Given** any batch
- **When** the counts are computed
- **Then** they partition it - every unit falls in exactly one state and the total equals the
  batch size, so a unit cannot fall through the classification into no count at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightCoverageCountsTests::test_the_three_counts_partition_the_batch
- **Verified:** yes (2026-08-03)

### AC3: a batch with one unreviewed unit names it

- **Given** a batch of many repaired units and exactly one never reviewed
- **When** the preflight runs
- **Then** it names that unit - the failure being repaired is a real gap hidden inside a crowd of
  false ones, so a count alone would leave the operator to find it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightCoverageCountsTests::test_the_single_unreviewed_unit_is_named_not_just_counted
- **Verified:** yes (2026-08-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0506 criterion 5, driven through the shipped preflight after LL0040, with the partition asserted so no unit escapes classification |
