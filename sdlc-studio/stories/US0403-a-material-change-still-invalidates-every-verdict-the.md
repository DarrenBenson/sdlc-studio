# US0403: a material change still invalidates every verdict, the distinction an operator declaration, recorded

> **Status:** Done
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0408
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0152
> **Points:** 2

## User Story

**As a** lead changing a Sprint Goal after a review
**I want** a materially different goal to invalidate every verdict as it does today, with the amendment-versus-material call recorded as my own declaration
**So that** the cheap amend path cannot be used to smuggle a different goal past a review it never had

## Acceptance Criteria

### AC1: A change declared material carries no verdict forward

- **Given** a recorded review of goal A
- **When** the goal is changed to goal B and the operator declares the change material rather than an amendment
- **Then** no verdict carries forward and every seat must review goal B, exactly as a plain new goal does today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MaterialGoalChangeTests::test_a_material_declaration_carries_no_verdict_forward
- **Verified:** yes (2026-07-23)

### AC2: The amendment-versus-material call is recorded as the operator's declaration

- **Given** the distinction cannot be made mechanically
- **When** a goal change is recorded
- **Then** the round stores whether the operator declared it an amendment or a material change, so the classification is an accountable declaration and not the tool's guess
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::MaterialGoalChangeTests::test_the_change_classification_is_recorded_as_an_operator_declaration
- **Verified:** yes (2026-07-23)

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code. Mutation-proven by hand: dropping the amendment carry-forward, letting a material change carry, inverting the needs-reconsult set, not storing the brief in the round, and ignoring the fields-file seats were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built and mutation-proven |
