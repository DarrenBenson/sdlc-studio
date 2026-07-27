# US0438: AGENTS.md stage: draft and confirm the agent instructions from the tool-neutral starter

> **Status:** Done
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 3

## User Story

**As an** operator in guided onboarding
**I want** the first stage to draft my `AGENTS.md` (and its `CLAUDE.md` import) from the tool-neutral starter and let me confirm before moving on
**So that** every agent that touches the repo inherits the discipline, and the flow advances only when I have reviewed it

## Acceptance Criteria

### AC1: the agents stage drafts the instructions from the tool-neutral starter

- **Given** a repo with no `AGENTS.md`
- **When** the agents stage runs
- **Then** it writes `AGENTS.md` (and the `CLAUDE.md` import) from the tool-neutral starter for the
  operator to review, and an existing file is left untouched (drafted once, never clobbered)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_agents_stage_drafts_the_instructions
- **Verified:** yes (2026-07-26)

### AC2: confirm and skip advance the runner through the guided command

- **Given** guided onboarding at its first stage
- **When** `init guided --confirm` then `init guided --skip` are run
- **Then** the first stage is recorded `done` and the runner advances, and the next is recorded
  `skipped` and the runner advances again - the flow moves only on the operator's word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_guided_confirm_and_skip_advance_the_runner
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
