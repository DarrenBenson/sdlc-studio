# US0593: A run whose only review verdicts are REJECT reports the closing-review item outstanding, never ran

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** operator reading a close report
**I want** the closing-review item to read verdicts rather than count passes
**So that** four rounds of which three rejected cannot report as `ran`

## Acceptance Criteria

### AC1: REJECT-only rounds report the item outstanding

- **Given** a run whose recorded review verdicts are all REJECT
- **When** the closing-review checklist item resolves
- **Then** it is OUTSTANDING, because the item counted passes rather than reading verdicts and reported `ran` over four rounds of which three rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_reject_only_rounds_are_outstanding

### AC2: an APPROVE covering every unit passes

- **Given** a run whose units are each covered by an APPROVE
- **When** the item resolves
- **Then** it passes - the control, so the item cannot be satisfied by one that never clears
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_an_approve_covering_every_unit_passes

### AC3: a REJECT followed by a later APPROVE passes

- **Given** a unit rejected in one round and approved in a later one
- **When** the item resolves
- **Then** it passes for that unit, because a REJECT is a verdict on a revision rather than a property of the work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ClosingReviewVerdictTests::test_a_later_approve_clears_an_earlier_reject

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
