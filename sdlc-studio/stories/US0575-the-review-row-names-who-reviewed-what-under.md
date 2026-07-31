# US0575: the review row names who reviewed what, under which seat, over how many lenses

> **Status:** Done
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** a reviewer of record deciding whether to sign a sprint off
**I want** the review row to say who reviewed what, under which seat, and over how many lenses
**So that** an under-covered round cannot read like a full one on the page I sign from

## Acceptance Criteria

### AC1: the review row names the covered units, the reviewer and the seat

- **Given** a run whose units carry recorded critic verdicts
- **When** the report is composed
- **Then** the review row names each covered unit with its reviewer and the seat that reviewer stood in, and a verdict recorded under no declared seat is reported as seat-less rather than silently rendered as a seat review - the persona lens drifting out of the loop must be visible
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistReviewRowTests::test_the_review_row_names_the_units_the_reviewer_and_the_seat
- **Verified:** yes (2026-07-30)

### AC2: a round under two lenses is reported as UNDER-COVERED

- **Given** a run reviewed by a single reviewer on a single lens
- **When** the report is composed
- **Then** the row states the lens count and marks the round under-covered, because the standing rule is at least two reviewers on distinct lenses with one of them the claims lens, and a small diff is not a licence to drop to one pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistReviewRowTests::test_a_single_lens_round_is_reported_as_under_covered
- **Verified:** yes (2026-07-30)

### AC3: a unit whose latest verdict is a REJECT is reported rejected, never covered

- **Given** a run holding a unit whose most recent recorded verdict is a REJECT
- **When** the report is composed
- **Then** that unit is reported as rejected rather than counted among the covered, so the page cannot launder a rejection into coverage the way the coverage gate did before BG0441 closed it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistReviewRowTests::test_a_rejected_unit_is_not_counted_as_covered
- **Verified:** yes (2026-07-30)

## Summary

A one-reviewer round must not read like a full one on the page the operator signs off from.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
