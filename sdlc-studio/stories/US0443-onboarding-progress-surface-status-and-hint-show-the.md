# US0443: Onboarding progress surface: status and hint show the checklist and the next step until the first plan

> **Status:** Review
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Epic:** EP0163
> **Points:** 3

## User Story

**As an** operator part-way through guided onboarding
**I want** `hint` to keep pointing me at the guided flow and name the next stage until I reach a first plan
**So that** the onboarding I can leave and resume always tells me the single next thing to do

## Acceptance Criteria

### AC1: while onboarding is in progress, hint resumes the guided flow

- **Given** a project where guided onboarding has started with an incomplete stage
- **When** the next-step hint is computed
- **Then** it points at `init guided` and names the next onboarding stage as the reason, taking
  precedence over the ordinary pipeline ladder - so the operator is walked to the first plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintTests::test_hint_resumes_guided_onboarding_while_in_progress
- **Verified:** yes (2026-07-27)
- **Verified:** yes (2026-07-26)

### AC2: once onboarding is complete or absent, the normal ladder resumes

- **Given** a project with no onboarding state, or one where every stage is done/skipped
- **When** the next-step hint is computed
- **Then** the onboarding branch yields nothing and the ordinary pipeline hint is used
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::OnboardingHintTests::test_completed_or_absent_onboarding_falls_through
- **Verified:** yes (2026-07-27)
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
