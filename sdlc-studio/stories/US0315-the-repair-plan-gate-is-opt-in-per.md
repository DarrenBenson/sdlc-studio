# US0315: The repair-plan gate is opt-in per project and OFF by default

> **Status:** Draft
> **Delivers:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py,.claude/skills/sdlc-studio/reference-config.md
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanConfigTests::test_an_absent_config_leaves_the_close_unchanged

### AC2: enabling it refuses an unplanned repair

- **Given** the same project with the gate enabled
- **When** the same unplanned repair is recorded
- **Then** it is refused, naming the key that enabled the gate so the operator can see what
  turned it on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanConfigTests::test_enabling_the_gate_refuses_an_unplanned_repair

### AC3: the key the documentation names is the key the code reads

- **Given** the config key as written in `reference-config.md`
- **When** the code resolves the gate's setting
- **Then** it reads that exact key, asserted by a test that takes the name from the
  documented spelling rather than restating it - BG0250 shipped a key four documents said
  was read and no code read, and a hand-copied constant in the test would reproduce it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RepairPlanConfigTests::test_the_documented_key_is_the_key_the_code_reads

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
