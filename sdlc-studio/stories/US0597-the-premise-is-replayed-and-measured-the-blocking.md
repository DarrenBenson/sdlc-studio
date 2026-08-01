# US0597: The premise is replayed and measured: the blocking-finding count before and after, and the lane run over the three diffs that motivated it

> **Status:** Review
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

### AC1: the lane names the prose-drift finding, and claims neither of the other two

- **Given** the real commit `67fc683f` and the tree as it stood at that point, where `changelog.d/BG0413.md` asserted the collapse signal exits 2 while the hunk moved the code to 3
- **When** the claim-drift lane is replayed over that commit against that tree
- **Then** it names `changelog.d/BG0413.md` - the exact stale claim BG0471 was filed for
- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_the_lane_names_the_prose_drift_finding
- **Verified:** yes (2026-08-01)

> **NARROWED, and the limit recorded (D0106).** The criterion first read "names all three". The
> replay this story exists to run is what disproved it: the three findings are not one class.
> BG0473 was a missing half of a two-half gate, which no prose checker should ever claim to
> detect, and BG0472 is a ticked-criterion defect owned by `ticked_over_untouched` and measured
> in US0584. A detector asserting coverage it does not have is the over-claim this sprint exists
> to stop, so the limit is stated rather than absorbed.

### AC2: it stays silent over a diff whose prose agrees

- **Given** a commit from the same range whose prose and code do not contradict
- **When** the lane is replayed over it
- **Then** it reports nothing, so the replay cannot be satisfied by a lane that flags everything - the control without which AC1 proves only that the lane fires

- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_a_clean_diff_replays_silent
- **Verified:** yes (2026-08-01)

### AC3: the before-and-after is recorded as a number, not a claim

- **Given** the recorded verdicts of RUN-01KYX375
- **When** the replay runs
- **Then** the blocking-finding count before and after the scoping rule is written to the evidence directory with the units it covers, so the sprint's justification is a figure a later reader can check rather than a sentence in a retro
- **Verify:** pytest tools/tests/test_claim_drift_replay.py::ReplayTests::test_the_before_and_after_is_recorded
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
