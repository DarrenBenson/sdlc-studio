# US0248: the close sign-off brief reads a sprint-level verdict as coverage rather than reporting every unit unreviewed; document the model

> **Status:** Done
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
- **Verify:** manual - retired by US0940: US0919 (ddcfc40c) deleted `critic.signoff_brief` and its `SignoffBriefTests`, so no brief renders a unit's coverage; `sprint sign`'s principal check (`sprint._principal_refusals`) asks who may sign, not how coverage reads, so it does not carry this claim
- **Verified:** manual (2026-09-26) - retired, superseded by US0919

### AC2: the coverage model is documented

- **Given** `reference-sprint.md`
- **When** an agent reads the closing-review section
- **Then** it documents that one sprint-level review is recorded once and satisfies the per-unit critiqued gate as coverage (sign-off still per unit)
- **Verify:** grep "still reads as coverage for a unit with no verdict of its own" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-26 | US0940 | AC1 retired in the D0259 pattern (US0919 deleted the brief). AC2 re-pointed at the sentence that now documents the model: a historical sprint-level row still reads as coverage for a unit with no verdict of its own. The 'recorded once' half went with US0918, which retired the batch-review writers, and 'sign-off still per unit' with US0919's one signature per run |
