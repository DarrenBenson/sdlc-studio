# US0595: A waiver records whether it was deliberate or its window had already expired, and the retro counts them apart

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** maintainer reading the record a year later
**I want** a waiver to record whether it was chosen or forced
**So that** a process failure is not laundered as a decision

## Acceptance Criteria

### AC1: a waiver records its kind

- **Given** two waivers, one taken deliberately and one for an item already unsatisfiable when it fired
- **When** each is recorded
- **Then** each carries its kind, so a process failure is not laundered as a decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_decisions.py::WaiverKindTests::test_a_waiver_records_its_kind

### AC2: the retro counts the two kinds apart

- **Given** a run holding one of each
- **When** the sprint report is composed
- **Then** it reports how many items expired before anyone was asked, separately from those set aside on purpose
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::WaiverKindTests::test_expired_and_deliberate_are_counted_apart

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
