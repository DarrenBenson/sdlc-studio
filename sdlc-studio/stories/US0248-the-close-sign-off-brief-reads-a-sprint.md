# US0248: the close sign-off brief reads a sprint-level verdict as coverage rather than reporting every unit unreviewed; document the model

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0080
> **Points:** 3

## User Story

**As a** reviewer of record reading the close sign-off brief
**I want** a unit covered by the sprint-level review to read as reviewed by that pass
**So that** the brief shows what the one full-diff review judged instead of reporting every covered unit as unreviewed

## Acceptance Criteria

### AC1: the brief reads a sprint-level verdict as coverage, not absence

- **Given** a unit with no per-unit verdict, covered by a recorded sprint-level review
- **When** the sign-off brief is composed
- **Then** the unit reads "covered by sprint-level review by <reviewer>" for both verdict and evidence, never "(no critic verdict recorded)"
- **Verify:** `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k SprintReviewBrief`

### AC2: the coverage model is documented

- **Given** `reference-sprint.md`
- **When** an agent reads the closing-review section
- **Then** it documents that one sprint-level review is recorded once and satisfies the per-unit critiqued gate as coverage (sign-off still per unit)
- **Verify:** `grep -q "recorded once, as coverage" .claude/skills/sdlc-studio/reference-sprint.md`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
