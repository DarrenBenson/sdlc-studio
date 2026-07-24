# US0425: the pass is intensity-scaled to batch size and records what the scaling skipped

> **Status:** Ready
> **Delivers:** RFC0050
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0158
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the pass is intensity-scaled to batch size

- **Given** a small batch and a large one
- **When** the pass runs over each
- **Then** the large batch receives more scrutiny than the small one, and the scaling rule is stated rather than emergent - the pass spends tokens before any value is delivered, on a sprint length already under complaint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticIntensityTests::test_a_larger_batch_receives_more_scrutiny

### AC2: what the scaling skipped is recorded

- **Given** a batch whose intensity setting bounded the pass
- **When** the pass finishes
- **Then** it names what it did not examine - a bounded pass that reports only what it found reads as complete coverage, and a silent cap is how a partial sweep gets mistaken for a full one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticIntensityTests::test_the_pass_names_what_the_intensity_cap_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
