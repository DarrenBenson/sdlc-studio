# US0558: A retro created by the scaffold and filled in as its template demonstrates passes retro validate without a rejection round-trip

> **Status:** Review
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/templates/reviews/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Epic:** EP0189
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an agent writing a close retro
**I want** the scaffold to demonstrate the shapes its own validator demands
**So that** the carried-set and disposition vocabulary are learned from the template rather than from three serial rejections

## Acceptance Criteria

### AC1: the scaffold's own output demonstrates every shape the validator demands

- **Given** the retro template as shipped
- **When** `retro validate` runs against a retro scaffolded from it with the demonstration content left in place
- **Then** it passes, so the template is a worked example rather than a set of headings
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::ScaffoldPassesItsValidatorTests::test_the_scaffolded_retro_passes_its_own_validator
- **Verified:** yes (2026-07-29)

### AC2: the carried-lessons shape is shown, not merely named

- **Given** the template's carried-lessons section
- **When** it is read
- **Then** it shows the bullet form the validator requires, so the numbered form that was rejected is not the natural thing to write
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::ScaffoldPassesItsValidatorTests::test_the_carried_lessons_section_demonstrates_the_accepted_shape
- **Verified:** yes (2026-07-29)

### AC3: the disposition vocabulary is demonstrated in the actions table

- **Given** the template's actions-raised table
- **When** it is read
- **Then** each accepted disposition form appears as a filled example, so the vocabulary is not first met in a refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::ScaffoldPassesItsValidatorTests::test_the_actions_table_demonstrates_the_disposition_vocabulary
- **Verified:** yes (2026-07-29)

### AC4: the demonstration content cannot be mistaken for a real entry

- **Given** a scaffolded retro whose demonstration rows were never replaced
- **When** the close reads it
- **Then** the unreplaced demonstration is reported, so a retro that passes structurally is not silently accepted as filled in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::ScaffoldPassesItsValidatorTests::test_unreplaced_demonstration_content_is_reported
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
