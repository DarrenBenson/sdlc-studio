# US0441: Personas stage: persona generate --team from the PRD and risk signals, accept or edit

> **Status:** Review
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 3

## User Story

**As an** operator in guided onboarding
**I want** the personas stage to grow my engineering team from the PRD and risk signals for me to accept or edit
**So that** the project-specific team that will build and review the work exists before the first sprint

## Acceptance Criteria

### AC1: the personas stage seeds the personas doc and directs team generation

- **Given** onboarding at the personas stage
- **When** the stage runs
- **Then** it seeds `sdlc-studio/personas.md` from the template (leaving an existing one untouched)
  and directs growing the team from the PRD and risk signals (`persona generate --team`), which the
  operator then accepts or edits
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_personas_stage_seeds_and_directs
- **Verified:** yes (2026-07-26)

### AC2: the personas stage advances the guided flow to decompose

- **Given** guided onboarding with agents, prd, trd and tsd confirmed
- **When** `init guided --confirm` is run at the personas stage
- **Then** the runner advances to `decompose`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_personas_stage_advances_to_decompose
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
