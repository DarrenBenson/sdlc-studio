# US1247: A unit that opts in gets the ownership line naming its Affects in its lane brief, and nothing else carries it

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0701
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/story.md, .claude/skills/sdlc-studio/templates/core/bug.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_ownership_line.py, changelog.d/US1247.md
> **Epic:** EP0343
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A unit that opts in gets the ownership line naming its Affects in its lane brief, and nothing else carries it
**So that** CR0701 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: An opted-in unit's lane brief carries the ownership line over its Affects

- **Given** a story and a bug that each declare the opt-in with the field `templates/core/story.md` and `templates/core/bug.md` document
- **When** `sprint.py lane brief --units <id>` renders each brief
- **Then** each brief carries the ownership line once: the builder owns the design of the files the unit's Affects declares, merges duplicated code within them, and files a change outside Affects as a finding instead of editing it. Fails on: a line that claims the whole codebase, or one that permits an edit outside Affects
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_ownership_line.py::OwnershipLineTests::test_an_opted_in_unit_carries_the_line_over_its_affects

### AC2: A unit that does not opt in carries no ownership line

- **Given** a unit with no opt-in field, and one whose opt-in field holds a value the template does not name
- **When** the lane brief is rendered for each
- **Then** the first brief is the text it was before this unit, and the second is refused naming the field and the value allowed. Fails on: the line on by default, or a misspelt opt-in silently read as off or on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_ownership_line.py::OwnershipLineTests::test_a_unit_that_does_not_opt_in_carries_no_line

### AC3: Nothing but the opted-in lane brief carries it

- **Given** the opted-in unit, this repository's AGENTS.md, CLAUDE.md and `.claude/agents/`, and the shipped `templates/agent-instructions.md` and `templates/agents/`
- **When** `critic.py brief` is rendered for the unit under each of the three seats and each file is read
- **Then** none carries the ownership line or the guide's owner-and-maintainer sentence (D0464). Fails on: a reviewer told it owns the design, or the sentence reaching an always-loaded file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_ownership_line.py::OwnershipLineTests::test_no_review_brief_definition_or_instruction_file_carries_it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
