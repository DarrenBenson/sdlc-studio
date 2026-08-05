# US0638: The close pre-flight runs the retro checklist it is about to be judged on

> **Status:** Ready
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0208
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The close pre-flight runs the retro checklist it is about to be judged on
**So that** CR0510 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: an outstanding checklist item is a pre-flight blocker

- **Given** a retro whose compulsory checklist holds an unanswered item
- **When** `close_preflight` runs against that retro id
- **Then** it returns not-ready with a blocker whose stage is `checklist`, naming the item and its remedy
- **Mutant:** delete the checklist call from the pre-flight - the run reads ready while the chain would stop at step 6
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightChecklistTests::test_an_unanswered_checklist_item_is_a_preflight_blocker

### AC2: one authority for the checklist, not a second copy of its rules

- **Given** a compulsory item added to `sprint_report.checklist` and nothing changed in `sprint.py`
- **When** the pre-flight runs against a retro that leaves it unanswered
- **Then** the new item is reported, because the pre-flight asks the checklist rather than restating its rows
- **Mutant:** enumerate the item names inside the pre-flight - the added row goes unreported and this test reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightChecklistTests::test_a_row_added_to_the_checklist_is_reported_without_touching_the_preflight

### AC3: every outstanding item in one pass, not the first one

- **Given** a retro with three unanswered compulsory items
- **When** the pre-flight runs once
- **Then** all three are reported together, so a second attempt is not needed to discover the second item
- **Mutant:** return after the first checklist blocker - the count assertion reddens
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightChecklistTests::test_every_outstanding_item_is_reported_in_one_pass

### AC4: still read-only, and a broken checklist does not hide the other blockers

- **Given** a checklist resolver that raises
- **When** the pre-flight runs
- **Then** the failure is reported as its own blocker and every other blocker is still returned, and the retro's recorded answers are unchanged on disk
- **Mutant:** let the exception propagate - the pre-flight dies and reports nothing at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightChecklistTests::test_a_raising_checklist_is_a_blocker_and_hides_nothing

### AC5: waivers are honoured here exactly as the chain honours them

- **Given** an item answered by a recorded waiver naming it
- **When** the pre-flight runs
- **Then** it is not reported, because a close that would proceed must not be told it cannot
- **Mutant:** treat every non-answered row as outstanding - a waived item blocks a closeable run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PreflightChecklistTests::test_a_waived_item_is_not_a_blocker

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
