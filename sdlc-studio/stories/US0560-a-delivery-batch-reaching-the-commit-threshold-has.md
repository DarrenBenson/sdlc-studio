# US0560: A delivery batch reaching the commit threshold has a defined review point, and the adversarial pass takes that batch's units as its surface

> **Status:** Done
> **Delivers:** CR0500
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0190
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** a maintainer whose sprint keeps discovering its defects after it has nominally ended
**I want** the adversarial pass to take a DELIVERY BATCH as its surface, at the cadence the project already commits on
**So that** a finding is delivery work in the batch that caused it, priced there and fixed by a context that still holds it

## Acceptance Criteria

### AC1: A delivery batch is a first-class span on the run state, opened at the previous boundary and closed when it is reviewed

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_a_batch_span_is_recorded_on_the_run_state
- **Verified:** yes (2026-07-29)

### AC2: `review_coverage` reports, per unit, whether an INDEPENDENT pass covers it - a per-unit critic verdict or a batch/sprint review whose reviewer differs from its author

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_coverage_reads_per_unit_and_batch_level_records
- **Verified:** yes (2026-07-29)

### AC3: A self-reviewed pass covers nothing: reviewer == author is not coverage, so the record cannot be satisfied by the context that wrote the code

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_a_self_review_is_not_coverage
- **Verified:** yes (2026-07-29)

### AC4: The review's surface is THAT BATCH's units: a review recorded over batch 1 leaves batch 2's units uncovered

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_a_review_does_not_cover_a_later_batch
- **Verified:** yes (2026-07-29)

### AC5: `sprint review-batch` records the pass over the open batch's units and closes the span, reusing the existing independence-proving critic record rather than a second one

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchBoundaryReviewTests::test_review_batch_records_and_closes_the_span
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
