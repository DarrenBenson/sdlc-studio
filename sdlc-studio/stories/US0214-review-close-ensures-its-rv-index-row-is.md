# US0214: review close ensures its RV index row is written

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0072
> **Depends on:** US0215
> **Points:** 2

## User Story

**As an** operator running the sprint close
**I want** the review close to write its own index row
**So that** the next step's reconcile does not halt the ceremony over a mechanical gap

## Acceptance Criteria

### AC1: The close writes the RV's index row

- **Given** a dated RV record with no row in `reviews/_index.md`
- **When** `review_prep close` runs
- **Then** the row is written as part of the close, using the shared meta-index helper so the house column order is honoured rather than the index being hand-edited.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_review_prep.CloseIndexRowTests.test_close_writes_the_index_row
- **Verified:** yes (2026-07-18)

### AC2: Reconcile finds no missing-row afterwards

- **Given** the same close has just run
- **When** reconcile inspects the reviews index
- **Then** it reports no missing-row drift - the close chain proceeds instead of stopping for a fix reconcile would have performed anyway.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_review_prep.CloseIndexRowTests.test_no_missing_row_drift_after_close
- **Verified:** yes (2026-07-18)

### AC3: A close whose row already exists is unchanged

- **Given** an RV that already has its index row
- **When** the close runs
- **Then** nothing is appended and no duplicate row appears, so a re-run is idempotent.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_review_prep.CloseIndexRowTests.test_existing_row_is_not_duplicated
- **Verified:** yes (2026-07-18)

### AC4: An indexing failure warns without losing the close

- **Given** an environment where the index write cannot be performed
- **When** the close runs
- **Then** the review state is still stamped and the failure is reported with the remedy, because the stamp is the close and indexing is a convenience on top of it.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_review_prep.CloseIndexRowTests.test_indexing_failure_still_stamps
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored; a seeded AC belonging to US0215 (review-current) removed - it is implemented under its owning story |
