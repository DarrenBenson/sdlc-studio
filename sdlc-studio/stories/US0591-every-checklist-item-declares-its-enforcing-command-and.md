# US0591: Every checklist item declares its enforcing command, and the close reports rather than gates on an expired window

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0197
> **Points:** 5

## User Story

**As a** operator whose close keeps stalling
**I want** each checklist item enforced where it can still be satisfied
**So that** a gate is not raised at a point where a waiver is its only exit

## Acceptance Criteria

### AC1: every item declares the command that enforces it

- **Given** the compulsory checklist as composed
- **When** each item is read
- **Then** each names the last command by which it can still be satisfied, so an item whose window closes before the close is not raised where it cannot be answered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistWindowTests::test_every_item_declares_its_enforcer

### AC2: an expired-window item is reported, not gated on

- **Given** a close reached with a window-bound item unsatisfied
- **When** the checklist resolves
- **Then** the item is REPORTED with the command that should have enforced it and does not hold the close, because a gate whose only exit at firing time is a waiver is a receipt rather than a gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistWindowTests::test_an_expired_item_reports_rather_than_gates

### AC3: a close-window item still gates

- **Given** an unwritten retro at the close
- **When** the checklist resolves
- **Then** it is OUTSTANDING and holds the close - the control, so moving windows does not disarm the items the close genuinely owns
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistWindowTests::test_a_close_window_item_still_gates

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
