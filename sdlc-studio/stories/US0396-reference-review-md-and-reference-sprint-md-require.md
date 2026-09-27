# US0396: reference-review.md and reference-sprint.md require at least two reviewers with distinct lenses including a claims lens, and record a single-reviewer round

> **Status:** Done
> **Delivers:** CR0397
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0148
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md

## User Story

**As a** reader of the review guidance
**I want** a round defined as at least two reviewers with distinct lenses, including a claims lens
**So that** a single-reviewer round is recorded as the exception it is

## Acceptance Criteria

### AC1: The review guidance states a round is at least two reviewers with distinct lenses whatever the diff

- **Given** the review guidance in reference-review.md and reference-sprint.md
- **When** the round definition is read
- **Then** The review guidance states a round is at least two reviewers with distinct lenses whatever the diff size, and names the claims lens as one.
- **Verify:** manual - retired by US0956: v6 reviews each unit with one independent reviewer, so a round is no longer defined as two reviewers on distinct lenses; the sprint report still counts the lenses and marks a single-lens round, and AC2 still holds
- **Verified:** manual (2026-09-27) - retired, superseded by US0956

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
| 2026-09-27 | Claude Opus 5.5 | AC1 retired by US0956 (D0259 pattern): the lean loop reviews each unit with one independent reviewer, so the two-reviewer round it pinned is gone from both docs; AC2 stands |
