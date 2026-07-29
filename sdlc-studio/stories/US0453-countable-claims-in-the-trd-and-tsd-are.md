# US0453: Countable claims in the TRD and TSD are checked against a census of what the repo actually ships

> **Status:** Review
> **Delivers:** RFC0056
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py, sdlc-studio/trd.md, sdlc-studio/tsd.md
> **Epic:** EP0167
> **Points:** 5

## User Story

**As a** reader trusting the TRD and TSD to describe the system that actually ships
**I want** their countable claims checked against a census of the repo
**So that** a number that has quietly stopped being true fails a check, instead of surviving until the next adversarial audit finds it

## Acceptance Criteria

### AC1: a countable claim that disagrees with the census fails, and an agreeing one passes

- **Given** a claim in the TRD or TSD marked derivable, such as the number of command types or of shipped scripts
- **When** the checker runs against a census of the repo
- **Then** a claim disagreeing with the census is reported with both the claimed and the counted value, and a claim agreeing with it passes
- **Verify:** pytest tools/tests/test_check_spec_claims.py::CountableClaimTests::test_a_claim_disagreeing_with_the_census_fails
- **Verified:** yes (2026-07-29)

### AC2: the expected count is derived from the tree, never stored

- **Given** the shipped set changes, a script being added or removed
- **When** the checker runs with no edit to the checker
- **Then** the expected number moves with the repo, because the check counts the tree rather than reading a total recorded earlier
- **Verify:** pytest tools/tests/test_check_spec_claims.py::CountableClaimTests::test_the_expected_count_is_derived_from_the_tree_not_stored
- **Verified:** yes (2026-07-29)

### AC3: a marked claim that cannot be checked is reported, not skipped

- **Given** a claim marked derivable whose value cannot be parsed, or one naming a census the checker does not know
- **When** it runs
- **Then** it reports that claim as unchecked and exits non-zero, rather than passing over it in silence
- **Verify:** pytest tools/tests/test_check_spec_claims.py::CountableClaimTests::test_an_unparseable_marked_claim_is_reported_not_skipped
- **Verified:** yes (2026-07-29)

### AC4: the check runs in the gate people already run

- **Given** the repo's quality gate
- **When** it runs
- **Then** the spec-claim check is one of its lanes, so drift is caught at the commit that causes it rather than at the next audit
- **Verify:** pytest tools/tests/test_check_spec_claims.py::GateLaneTests::test_the_spec_claim_check_is_a_gate_lane
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
