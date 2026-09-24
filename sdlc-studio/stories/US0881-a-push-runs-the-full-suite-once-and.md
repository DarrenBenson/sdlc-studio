# US0881: A push runs the full suite once, and CI runs it once

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-push, .github/workflows/lint.yml, tools/boundary_roster.py, AGENTS.md, tools/tests/test_lean_push.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/boundary.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .githooks/commit-msg, tools/skill-tests.sh, tools/tests/test_check_spec_claims.py, tools/tests/test_pre_push_hook.py
> **Epic:** EP0261
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** developer pushing to main
**I want** the push and CI to run the full suite once each
**So that** a push takes minutes, not a quarter of an hour, and CI stops paying for the suite twice

## Acceptance Criteria

- **AC1:** Given gate.py --boundary push, then it runs the full suite once plus the core gate lanes, and does not run module-alone, revert-check or release-rehearsal
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_push_runs_the_suite_once
  - **Verified:** yes (2026-09-24)
- **AC2:** Given gate.py --boundary release, then module-alone and release-rehearsal still run - the heavy lanes stay at the tag
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_the_release_boundary_keeps_the_heavy_lanes
  - **Verified:** yes (2026-09-24)
- **AC3:** Given .github/workflows/lint.yml, then the ci job runs the skill suite exactly once, under coverage
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_ci_runs_the_suite_once
  - **Verified:** yes (2026-09-24)
- **AC4:** Given the forge returns a stale red run for main once, when the pre-push hook reads it, then it re-reads before refusing and does not refuse when the re-read is green (BG0709)
  - **Verify:** pytest tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
