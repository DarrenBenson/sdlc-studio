# US0585: The claim-drift lane runs in the commit gate as advisory, and its yield over one sprint is recorded before any decision to make it block

> **Status:** Draft
> **Delivers:** CR0517
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/tests/test_precommit_lane_order.py, AGENTS.md
> **Epic:** EP0195
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the lane runs in the commit gate and reports without blocking

- **Given** a staged diff carrying a claim contradiction
- **When** `git commit` is run for real in a fixture clone with the shipped hooks enabled
- **Then** the finding is printed and the commit LANDS, because a new lane on a gate already over its ceiling must earn a block on measured evidence rather than assertion
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::LaneTests::test_the_lane_reports_and_does_not_block

### AC2: the lane is named in the gate roster

- **Given** AGENTS.md's pre-commit lane roster
- **When** the lane ships
- **Then** the roster names it, and `test_check_spec_claims.py` pins that naming, so the list cannot silently exempt what it forgot
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::LaneTests::test_the_lane_is_named_in_the_gate_roster

### AC3: its yield is recorded before any decision to block

- **Given** one sprint's worth of runs with the lane advisory
- **When** the sprint report is composed
- **Then** it carries the count of findings the lane raised and how many became filed defects, so the decision to make it blocking is taken against measurement rather than impression
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::LaneTests::test_the_yield_is_recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
