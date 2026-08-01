# US0597: The premise is replayed and measured: the blocking-finding count before and after, and the lane run over the three diffs that motivated it

> **Status:** Draft
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_claim_drift_replay.py, sdlc-studio/retros/evidence/claim-drift-replay.json, tools/check_spec_claims.py
> **Epic:** EP0195
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator funding this sprint
**I want** the premise it rests on measured rather than asserted
**So that** a mechanism is not shipped on a claim nobody checked

### AC1: the lane names the three findings that motivated it

- **Given** the real diffs of BG0471, BG0472 and BG0473 - the three blocking findings the corrected review loop returned, each a stale claim in prose contradicted by code in the same diff
- **When** the claim-drift lane is replayed over them
- **Then** it names all three, because the whole case for the lane is that these were decidable from the diff alone and instead cost an adversarial review round each
- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_the_lane_names_the_three_motivating_findings

### AC2: it stays silent over a diff whose prose agrees

- **Given** a commit from the same range whose prose and code do not contradict
- **When** the lane is replayed over it
- **Then** it reports nothing, so the replay cannot be satisfied by a lane that flags everything - the control without which AC1 proves only that the lane fires

- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_a_clean_diff_replays_silent

### AC3: the before-and-after is recorded as a number, not a claim

- **Given** the recorded verdicts of RUN-01KYX375
- **When** the replay runs
- **Then** the blocking-finding count before and after the scoping rule is written to the evidence directory with the units it covers, so the sprint's justification is a figure a later reader can check rather than a sentence in a retro
- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_the_before_and_after_is_recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
