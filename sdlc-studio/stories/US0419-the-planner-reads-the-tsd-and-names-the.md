# US0419: the planner reads the TSD and names the risk areas the batch touches

> **Status:** Done
> **Delivers:** RFC0049
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0157
> **Points:** 5

## User Story

**As an** operator reading a sprint plan
**I want** the planner to read the TSD and name the risk areas the batch touches
**So that** risk comes from the strategy document rather than from a collapsed WSJF score

## Acceptance Criteria

### AC1: the planner reads the TSD and names the risk areas the batch touches

- **Given** a batch whose units touch areas the TSD identifies as risk-bearing
- **When** `sprint plan` runs
- **Then** the plan names each TSD risk area the batch touches, resolved from the units' `Affects` against the TSD - not from the QA seat's WSJF score, which is collapsed into an ordering number and discarded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_the_plan_names_the_tsd_risk_areas_the_batch_touches
- **Verified:** yes (2026-07-24)

### AC2: a batch touching no risk area says so, rather than printing nothing

- **Given** a batch of purely documentation units
- **When** the plan runs
- **Then** it states that no TSD risk area is touched - an empty section is indistinguishable from a lane that did not run, which is the reporting failure US0354's review found
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_no_risk_area_is_stated_explicitly_not_left_blank
- **Verified:** yes (2026-07-24)

### AC3: the TSD is read, not assumed

- **Given** a TSD with a risk area added since the last plan
- **When** the plan runs
- **Then** the new area appears - the strategy is derived from the document at plan time rather than from a list baked into the planner
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyTests::test_a_newly_added_risk_area_appears_without_a_code_change
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
