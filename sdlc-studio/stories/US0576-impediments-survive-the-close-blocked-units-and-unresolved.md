# US0576: impediments survive the close: blocked units and unresolved operator decisions are reported with what is in the way

> **Status:** Review
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** the next agent picking up after a close
**I want** every blocker and every unanswered operator question carried into the report
**So that** an impediment recorded mid-run is not rediscovered from scratch next sprint

## Acceptance Criteria

### AC1: a blocked unit is reported with what blocked it

- **Given** a run whose batch holds a unit at Blocked
- **When** the report is composed
- **Then** the impediments row names the unit and the blocker recorded against it, and a unit blocked with no recorded blocker is named as such rather than dropped - three failed green attempts and a stall nobody wrote down read identically once the session ends
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistImpedimentTests::test_a_blocked_unit_is_reported_with_its_blocker
- **Verified:** yes (2026-07-30)

### AC2: an unresolved operator decision is reported with its question

- **Given** a run carrying deferred decisions, one resolved and one still open
- **When** the report is composed
- **Then** only the open one is reported as an impediment, carrying its question verbatim, so the operator meets the question on the close page instead of in a ledger nobody opened
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistImpedimentTests::test_an_unresolved_decision_is_reported_with_its_question
- **Verified:** yes (2026-07-30)

### AC3: no impediments reads differently from not checked

- **Given** a run with nothing blocked and no open decision, and a second run whose ledger cannot be read
- **When** each report is composed
- **Then** the first states there were none and the second states the impediments could not be read, because a scan that failed and a scan that found nothing call for opposite responses and must never render the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistImpedimentTests::test_none_and_unreadable_do_not_render_the_same
- **Verified:** yes (2026-07-30)

## Summary

A blocker recorded mid-run is lost at the close, so the next run rediscovers it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
