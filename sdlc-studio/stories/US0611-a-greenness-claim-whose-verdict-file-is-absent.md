# US0611: A greenness claim whose verdict file is absent or stale against HEAD is refused by the commit gate

> **Status:** Ready
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

### AC1: an absent or stale verdict refuses the claim

- **Given** a commit claiming the suite is green whose verdict file is missing, or whose recorded sha is not HEAD
- **When** the gate runs
- **Then** it refuses naming which, because an unverifiable claim of greenness is the failure this exists to remove
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_an_absent_or_stale_verdict_is_refused

### AC2: a current green verdict passes

- **Given** a verdict file recording exit 0 at HEAD
- **When** the gate runs
- **Then** it passes, so the check cannot be satisfied by one that refuses every commit
- **Verify:** pytest tools/tests/test_run_suite.py::GateTests::test_a_current_green_verdict_passes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
