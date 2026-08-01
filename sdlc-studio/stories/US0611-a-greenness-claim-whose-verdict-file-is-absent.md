# US0611: A greenness claim whose verdict file is absent or stale against HEAD is refused by the commit gate

> **Status:** Review
> **Delivers:** CR0519
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, .githooks/pre-commit, tools/tests/test_run_suite.py
> **Epic:** EP0201
> **Points:** 3

## User Story

**As a** maintainer of the commit gate
**I want** a greenness claim refused when its verdict file is absent or stale
**So that** the rule is enforced by the command people run rather than by an agent's memory

## Acceptance Criteria

### AC1: an ABSENT verdict refuses the claim

- **Given** a commit claiming the suite is green with no verdict file at all
- **When** the check runs
- **Then** it refuses, because absent must never read as pass - that is the fail-open shape, indistinguishable from a suite nobody ran
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_an_absent_verdict_is_refused
- **Verified:** yes (2026-08-01)

### AC2: a STALE verdict refuses the claim

- **Given** a verdict recorded at an earlier commit than HEAD
- **When** the check runs
- **Then** it refuses naming both shas, because a verdict from three commits ago exists and looks current, which is worse than none
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_a_stale_verdict_is_refused
- **Verified:** yes (2026-08-01)

### AC3: a RED verdict at the right sha refuses the claim

- **Given** a current verdict recording a non-zero exit code
- **When** the check runs
- **Then** it refuses, so freshness alone is not mistaken for greenness
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_a_red_verdict_is_refused
- **Verified:** yes (2026-08-01)

### AC4: the check is wired into the commit-msg hook and ends it

- **Given** the shipped `.githooks/commit-msg`
- **When** it is read
- **Then** it invokes the check and REFUSES there, rather than setting a flag section 2 resets - a lane that sets a variable nobody reads is the library-not-lane defect in a shell script
- **Verify:** pytest tools/tests/test_run_suite.py::CommitClaimLaneTests::test_the_lane_is_wired_into_the_hook
- **Verified:** yes (2026-08-01)

### AC5: a current green verdict passes

- **Given** a verdict file recording exit 0 at HEAD
- **When** the gate runs
- **Then** it passes, so the check cannot be satisfied by one that refuses every commit
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_a_current_green_verdict_passes
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
