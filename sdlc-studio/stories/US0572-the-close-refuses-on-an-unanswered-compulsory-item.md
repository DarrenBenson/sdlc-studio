# US0572: the close REFUSES on an unanswered compulsory item and names which one

> **Status:** Draft
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0192
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator relying on a compulsory checklist
**I want** the close to refuse on an unanswered item and name it
**So that** a practice that is compulsory in prose is compulsory in fact

## Acceptance Criteria

### AC1: the close REFUSES on an unanswered compulsory item and names it

- **Given** a run whose report leaves a compulsory item unanswered
- **When** the close runs
- **Then** it refuses and names the item - three previous attempts to make a practice compulsory by writing it down (the seat ceremony, the waiver shrink rule, the review standing practices) were each skipped or unenforced, so a checklist nothing holds is the state this replaces
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CompulsoryItemTests::test_the_close_refuses_on_an_unanswered_item_and_names_it

### AC2: every compulsory item has exactly ONE authority

- **Given** the compulsory set
- **When** the report is assembled
- **Then** each item is either derived from the tree or asked of the operator, never both and never neither, and a guard asserts the set is fully covered - an item with no authority is one that silently passes, which is how the seat ceremony was bypassed without a warning
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CompulsoryItemTests::test_every_compulsory_item_has_exactly_one_authority

### AC3: waiving a compulsory item is RECORDED, never implicit

- **Given** a run that must close without one compulsory item
- **When** the item is waived
- **Then** the waiver is recorded with its reason and authoriser on the same terms as a conformance waiver, so closing without an item and forgetting it are different events in the record
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::CompulsoryItemTests::test_waiving_a_compulsory_item_is_recorded_with_a_reason

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
