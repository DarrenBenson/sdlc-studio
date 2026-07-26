# US0442: Decompose to the first sprint plan: epics and stories, landing the user at a ready plan

> **Status:** Review
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0163
> **Points:** 3

## User Story

**As an** operator finishing guided onboarding
**I want** the last stages to decompose my PRD into epics and stories and land me at a ready first sprint plan
**So that** onboarding ends where delivery begins - I answer the prompts and I am ready to plan a sprint

## Acceptance Criteria

### AC1: the decompose and plan stages direct the last steps to a first plan

- **Given** onboarding at the decompose stage, then the plan stage
- **When** each stage runs
- **Then** the decompose stage directs breaking the PRD into epics and stories (`epic`, `story`),
  and the plan stage directs the first sprint plan (`sprint plan`) - the two agent-driven steps
  that turn the spec into a ready plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_decompose_and_plan_stages_direct
- **Verified:** yes (2026-07-26)

### AC2: confirming every stage completes onboarding at a ready first plan

- **Given** guided onboarding with every earlier stage confirmed
- **When** the decompose and plan stages are confirmed
- **Then** no stage remains incomplete and `init guided` reports onboarding complete - ready for the
  first sprint plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_confirming_all_stages_completes_onboarding
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
