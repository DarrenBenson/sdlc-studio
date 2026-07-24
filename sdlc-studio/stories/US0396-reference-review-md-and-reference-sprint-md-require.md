# US0396: reference-review.md and reference-sprint.md require at least two reviewers with distinct lenses including a claims lens, and record a single-reviewer round

> **Status:** Draft
> **Delivers:** CR0397
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0148
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: The review guidance states a round is at least two reviewers with distinct lenses whatever the diff

- **Given** the review guidance in reference-review.md and reference-sprint.md
- **When** the round definition is read
- **Then** The review guidance states a round is at least two reviewers with distinct lenses whatever the diff size, and names the claims lens as one.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::ReviewRoundLensesDocTests::test_a_round_is_two_reviewers_on_distinct_lenses_whatever_the_diff .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::ReviewRoundLensesDocTests::test_the_sprint_close_states_the_same_two_lens_round
- **Verified:** yes (2026-07-24)

### AC2: Where a round runs with one reviewer, the review record says so

- **Given** the review guidance in both docs
- **When** the single-reviewer case is read
- **Then** Where a round runs with one reviewer, the review record says so.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::ReviewRoundLensesDocTests::test_a_single_reviewer_round_is_recorded_as_such
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
