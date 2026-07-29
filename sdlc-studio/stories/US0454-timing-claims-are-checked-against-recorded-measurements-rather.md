# US0454: Timing claims are checked against recorded measurements rather than restated from memory

> **Status:** Review
> **Delivers:** RFC0056
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py, sdlc-studio/tsd.md
> **Epic:** EP0167
> **Points:** 3

## User Story

**As a** reader deciding whether to run the suite from what the TSD promises about it
**I want** timing claims checked against what the gate actually recorded
**So that** a claim like 'runs in under a minute' cannot outlive the measurement that once made it true

## Acceptance Criteria

### AC1: a timing claim contradicted by the recorded measurement fails

- **Given** a timing claim in the TSD and a recorded measurement history showing a materially different duration
- **When** the checker runs
- **Then** it fails, naming the claim, the bound it asserts and the measured value that contradicts it
- **Verify:** pytest tools/tests/test_check_spec_claims.py::TimingClaimTests::test_a_timing_claim_contradicted_by_measurement_fails
- **Verified:** yes (2026-07-29)

### AC2: an absent measurement is unverifiable, never a pass

- **Given** a timing claim for which no measurement has been recorded yet
- **When** the checker runs
- **Then** it reports the claim as unverifiable and says so plainly, rather than treating a missing measurement as agreement
- **Verify:** pytest tools/tests/test_check_spec_claims.py::TimingClaimTests::test_absent_measurement_is_unverifiable_not_a_pass
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
