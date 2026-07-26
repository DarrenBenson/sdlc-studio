# US0439: PRD stage: greenfield prd create or brownfield prd generate, draft-then-confirm

> **Status:** Review
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 5

## User Story

**As an** operator in guided onboarding
**I want** the PRD stage to fork on my project's path - interview me for a new project, read my code for an existing one
**So that** the spec is authored the right way for what I actually have, without me choosing a command

## Acceptance Criteria

### AC1: the PRD stage seeds the scaffold and forks on the classified path

- **Given** onboarding classified as greenfield, and separately as brownfield
- **When** the PRD stage runs
- **Then** it seeds the `sdlc-studio/prd.md` scaffold (leaving an existing one untouched) and returns
  the path-appropriate directive: greenfield names the interview (`prd create`), brownfield names
  reading the code (`prd generate`, validated downstream by `code verify`)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_prd_stage_forks_greenfield_and_brownfield
- **Verified:** yes (2026-07-26)

### AC2: the PRD stage runs as part of the guided flow after agents

- **Given** guided onboarding with the agents stage confirmed
- **When** `init guided` runs
- **Then** the current stage is `prd`, its directive is surfaced, and confirming it advances to `trd`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_prd_stage_is_reached_and_advances
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
