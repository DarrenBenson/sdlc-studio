# US0582: The shipped doctrine states the review scope rule, so a consuming project inherits the bound and not just the ceremony

> **Status:** Review
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, tools/doctrine_review_scope.py, tools/tests/test_doctrine_review_scope.py
> **Epic:** EP0194
> **Points:** 2

## User Story

**As a** maintainer of a project that installs this skill
**I want** the review scope rule stated in the shipped doctrine
**So that** a consuming project inherits the bound and not only the ceremony

## Acceptance Criteria

### AC1: the doctrine states the review scope rule

- **Given** `reference-doctrine.md` as shipped
- **When** it is read
- **Then** it states that a review judges the unit's own declared `Affects` against the run's base ref, and that only a regression or a newly introduced defect blocks
- **Verify:** pytest tools/tests/test_doctrine_review_scope.py::DoctrineTests::test_the_scope_rule_is_stated
- **Verified:** yes (2026-08-01)

### AC2: the guard discriminates and its own history cannot satisfy it

- **Given** a guard asserting the doctrine carries the rule
- **When** the stating passage is deleted while the Revision History row describing this change remains
- **Then** the guard goes red, because a whole-file substring satisfied by the row describing the change is the defect BG0457 records
- **Verify:** pytest tools/tests/test_doctrine_review_scope.py::DoctrineTests::test_deleting_the_passage_reddens_the_guard
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
