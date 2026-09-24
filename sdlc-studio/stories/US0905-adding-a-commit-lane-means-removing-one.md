# US0905: Adding a commit lane means removing one

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_lean_commit_lanes.py, tools/tests/test_precommit_lane_order.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** developer proposing a new commit check
**I want** a cap on how many lanes a commit runs, so a new lane has to displace one
**So that** the commit lane count can no longer only grow, which is how 18 lanes accumulated

## Acceptance Criteria

- **AC1:** Given the lanes a commit runs (both hooks' `--list` output plus the gate's per-commit lanes), when their count exceeds the cap written in `test_lean_commit_lanes.py` (the count once this sprint's deletions land), then the test fails naming every lane and saying one must go for one to come in; at or under the cap it passes - both shown on a fixture hook with one lane added
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_a_lane_over_the_cap_fails_naming_the_trade
- **AC2:** Given the cap, then it replaces the hand-maintained exact lane sets (`EXPECTED_LANES`, `MSG_HOOK_LANES`) in `test_precommit_lane_order.py` that every lane change had to edit: `LaneOrderTests::test_no_lane_is_lost_in_the_reorder` is deleted and US0268's criterion naming it is retired in the D0259 pattern, so the suite holds one lane pin rather than two
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_the_cap_retires_the_exact_lane_pins

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
