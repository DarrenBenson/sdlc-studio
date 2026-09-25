# US0315: The repair-plan gate is opt-in per project and OFF by default

> **Status:** Done
> **Verification depth:** functional - node-addressed tests in test_repair_plan.py / test_critic.py, all green; EP0106 mutation-proven (11 mutants across record_repair_plan, review, gate, pin, provenance, all killed)
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repair_plan.py,.claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0106
> **Points:** 2

## User Story

**As an** operator of an existing project
**I want** the repair-plan gate off until I ask for it
**So that** installing this version does not change how my next close behaves

## Acceptance Criteria

### AC1: an absent config leaves the close exactly as it is

- **Given** a project whose `.config.yaml` declares nothing about the repair-plan gate
- **When** a REJECT is repaired with no plan at all
- **Then** nothing is refused and no new artefact is required, so an upgrading project sees
  no behaviour change
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

### AC2: enabling it refuses an unplanned repair

- **Given** the same project with the gate enabled
- **When** the same unplanned repair is recorded
- **Then** it is refused, naming the key that enabled the gate so the operator can see what
  turned it on
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

### AC3: the key the documentation names is the key the code reads

- **Given** the config key as written in `reference-config.md`
- **When** the code resolves the gate's setting
- **Then** it reads that exact key, asserted by a test that takes the name from the
  documented spelling rather than restating it - BG0250 shipped a key four documents said
  was read and no code read, and a hand-copied constant in the test would reproduce it
- **Verify:** manual - retired by US0913: the repair-plan gate and repair_plan.py were deleted; a repair closes on green criteria and a round-2 APPROVE
- **Verified:** manual (2026-09-25) - retired, superseded by US0913

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
