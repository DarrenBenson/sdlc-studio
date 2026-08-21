# US0674: revert-check runs as a gate lane, so a unit whose tests reach nothing is refused rather than reported

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_check_spec_claims.py, AGENTS.md
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check runs as a gate lane, so a unit whose tests reach nothing is refused rather than reported
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project running the gate, when `gate.py` executes, then `revert-check` runs as a named lane and a unit whose verifiers stay green after the revert BLOCKS it - the lane refuses rather than reports, which is the whole difference from an advisory version of the same idea
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_lane_blocks_a_unit_whose_verifiers_stay_green
- [ ] **AC2** Given the pre-commit lane roster AGENTS.md documents, when `tools/tests/test_check_spec_claims.py` runs, then it names `revert-check` - a lane absent from the roster is one nobody notices losing, which is LL0013 and is why that pinning test exists
  - **Verify:** pytest tools/tests/test_check_spec_claims.py -k revert_check
- [ ] **AC3** Given the lane's measured cost, when the gate budget is reported, then the lane's contribution appears against the declared per-test rate - a new blocking check on a gate already over its ceiling earns its place on a number rather than on assertion, which is the rule `claim-drift` already ships advisory under
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_lane_reports_its_cost_against_the_declared_rate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
