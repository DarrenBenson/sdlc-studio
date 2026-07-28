# US0449: The batch and refine minting paths resolve the persona the same way, so the commands that mint most stories are covered too

> **Status:** Done
> **Delivers:** CR0425
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0166
> **Points:** 2

## User Story

**As an** operator whose stories are minted in bulk rather than one at a time
**I want** the batch and refine minting paths to resolve the persona exactly as `new` does
**So that** the resolution lives in the commands people actually run, not only in the one path a reader is told to use

## Acceptance Criteria

### AC1: batch resolves the persona per story exactly as new does

- **Given** a batch minting several stories, some naming a persona and some omitting it
- **When** it runs
- **Then** each story's Persona line is resolved by the same rules `new` applies - the declared Primary by default, a warning on an unregistered name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::BatchPersonaResolutionTests::test_batch_resolves_the_persona_per_story
- **Verified:** yes (2026-07-27)

### AC2: stories minted by refine carry a resolved persona

- **Given** a request decomposed into stories by `refine`
- **When** they are minted
- **Then** each carries a Persona line resolved from the registry rather than none at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::RefinePersonaTests::test_refined_stories_carry_a_resolved_persona
- **Verified:** yes (2026-07-27)

### AC3: the three minting paths agree, proven by comparing them rather than asserting each alone

- **Given** the `new`, `batch` and `refine` paths under identical registry conditions
- **When** each mints a story
- **Then** all three produce the same resolved Persona line, proven by one test that compares the three outputs and fails when any path diverges
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::RefinePersonaTests::test_new_batch_and_refine_agree_on_the_resolved_persona
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
