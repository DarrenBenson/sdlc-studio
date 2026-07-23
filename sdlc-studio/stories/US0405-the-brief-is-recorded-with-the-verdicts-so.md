# US0405: the brief is recorded with the verdicts so a thin brief is visible

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0409
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0153
> **Points:** 2

## User Story

**As a** reviewer of record reading a goal review
**I want** the brief that was given recorded alongside the seat verdicts
**So that** a review that found nothing is visible as a thin brief rather than mistaken for a clean goal

## Acceptance Criteria

### AC1: The brief given is stored in the same round as the verdicts

- **Given** a brief was emitted for the batch
- **When** the seat verdicts are recorded
- **Then** the brief is stored in the same round as the verdicts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefRecordedTests::test_the_brief_is_stored_with_the_recorded_verdicts

### AC2: The recorded brief is readable back with the round

- **Given** a recorded review carrying its brief
- **When** the round is read back
- **Then** the brief is returned with it, so a thin verdict can be told from a thin brief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeatBriefRecordedTests::test_the_recorded_brief_is_readable_back_with_the_round

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
