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

## Test-plan notes

Written after a plan review rejected the first draft. What the tests must do beyond asserting
a state, each recorded because it is what makes the named mutant lethal:

1. **AC1 checks the window's VALUE, not its presence.** A presence assertion is killed by
   deleting a key, but an implementation that stamps every row `sprint close` also satisfies
   it and delivers nothing - AC2 then has no real expired row to find. The test asserts that
   the pre-close rows (`goal-seat-reviewed`, `batch-groomed`, `reconciled-before-plan`) carry
   a window that is NOT the close, and it extends `cycle_drift`'s existing resolvability check
   from `command` to `window`, so a window naming a verb no shipped script exposes reddens.
2. **AC2 asserts the row is REPORTED, not merely un-held.** Dropping the state out of
   `_OUTSTANDING` alone leaves `outstanding` and `pending_in_close` both empty and the close
   printing `none outstanding` - the row vanishes instead of being reported. The test reads the
   rendered checklist and asserts the expired row appears there carrying its enforcing command.
   Note `render_checklist`'s `mark` lookup is exhaustive and raises on an unknown state, so the
   renderer must be extended; that forces a line to exist, not that it names the command.
3. **AC3 carries its positive control**: a written retro resolves RAN and appears in no bucket.
   Without it, an implementation that reports everything outstanding passes AC3.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change sprint_report.py to stamp every CHECKLIST row's window with the close, so no row has a window that can expire | every item declares the command that enforces it |
| AC2 | delete the expired bucket's line from `render_checklist` in sprint_report.py, so a row past its window disappears instead of being reported | an expired-window item is reported, not gated on |
| AC3 | change `_expired` in sprint_report.py to return True unconditionally | a close-window item still gates |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
