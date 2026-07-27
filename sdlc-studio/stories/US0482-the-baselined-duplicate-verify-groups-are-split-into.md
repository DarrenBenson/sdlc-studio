# US0482: The baselined duplicate Verify groups are split into discriminating selectors

> **Status:** Ready
> **Delivers:** CR0445
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Points:** 5

## User Story

**As a** reader taking a Done story's evidence as proof of the criterion beside it
**I want** each acceptance criterion to name a selector that distinguishes it from its neighbours
**So that** a green stamp means that criterion was checked, not that some criterion in the story was

## Acceptance Criteria

### AC1: no intra-story duplicate group remains

- **Given** the 13 duplicate groups confined within a single story
- **When** the lint runs over the workspace
- **Then** it reports no intra-story duplicate group, each having been split into per-criterion selectors
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_no_intra_story_duplicate_group_remains

### AC2: the groups no collection can answer are named with the reason

- **Given** the four groups whose selectors cannot be resolved by collection
- **When** the lint runs
- **Then** each is reported individually with why it is unanswerable, rather than being absorbed into a count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_unanswerable_groups_are_named_with_their_reason

### AC3: the ratchet still refuses a new duplicate after the burn-down

- **Given** an emptied baseline
- **When** a story introducing a fresh duplicate group is added
- **Then** the ratchet refuses it, proving the burn-down did not disarm the guard that protects it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_the_ratchet_still_refuses_a_new_duplicate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
