# US0437: Guided init orchestrator skeleton: resumable onboarding state, greenfield/brownfield detection, and the draft-then-confirm stage runner

> **Status:** Done
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 5

## User Story

**As a** new or returning operator running `init`
**I want** the guided onboarding to remember where I am, know whether my repo is greenfield or brownfield, and advance only when I confirm
**So that** a long onboarding I can leave and resume drives me stage by stage to a first sprint plan, instead of a one-shot scaffold I then have to sequence by hand

## Acceptance Criteria

### AC1: onboarding state is created and resumes from the first incomplete stage

- **Given** a project where guided onboarding has started
- **When** the onboarding state is read (and re-read after some stages complete)
- **Then** `sdlc-studio/.local/onboarding.json` records the ordered stages each with a status
  (pending/done/skipped), and resuming returns the FIRST incomplete stage - never restarting from
  the top nor skipping past unfinished work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_onboarding_state_resumes_from_first_incomplete_stage
- **Verified:** yes (2026-07-26)

### AC2: the repo is classified greenfield or brownfield

- **Given** a repo that is empty/near-empty, and separately one that already contains source
- **When** the orchestrator classifies the onboarding path
- **Then** it returns `greenfield` for the empty repo and `brownfield` for the one with existing
  code, and records the classification so the PRD stage can fork on it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_classifies_greenfield_and_brownfield
- **Verified:** yes (2026-07-26)

### AC3: the stage runner advances on confirm, records a skip, and resets

- **Given** onboarding state with pending stages
- **When** a stage is confirmed done, another is skipped, and `--reset` is applied
- **Then** a confirmed stage advances the runner; a skipped stage is recorded `skipped` (never
  silently dropped); and reset returns every stage to `pending`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_stage_runner_confirm_skip_and_reset
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
