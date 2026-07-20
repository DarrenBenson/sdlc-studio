# US0274: the preflight covers the apply-signoff prerequisites per unit, not just the gate lanes

> **Status:** Draft
> **Delivers:** CR0359
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0089
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the apply-signoff prerequisites are covered, not just the gate lanes

- **Given** a run whose batch units lack a recorded critic verdict, adversarial evidence, or an
  independent reviewer-of-record sign-off
- **When** the pre-flight runs
- **Then** each missing prerequisite is named per unit, alongside the gate lanes - these surface
  only after the whole chain has passed today, which is what made a close take four runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_names_missing_signoff_prerequisites
- **Verified:** yes (2026-07-20)

### AC2: a unit covered by a sprint-level review is not reported as missing

- **Given** a batch unit with no per-unit verdict but covered by an independent sprint-level
  full-diff review
- **When** the pre-flight runs
- **Then** it is NOT reported as missing its critique, because sprint coverage satisfies that gate
  and a pre-flight that over-reports is as untrustworthy as one that under-reports
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_accepts_sprint_level_coverage
- **Verified:** yes (2026-07-20)

### AC3: the check asks the real authority, never its own copy of the rule

- **Given** the sign-off rules enforced by `critic`
- **When** the pre-flight evaluates them
- **Then** it calls `critic`'s own predicates rather than reimplementing independence, so the
  pre-flight and the gate cannot drift apart and disagree about the same unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_delegates_to_critic
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
