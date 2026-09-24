# US0880: A commit's tests finish inside a 90-second budget

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, AGENTS.md, tools/gate_timing.py, tools/tests/test_gate_timing.py, tools/tests/test_lean_commit_lanes.py, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_budget_recording.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_precommit_selection.py
> **Epic:** EP0261
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** the commit to run only the tests its change can reach, in parallel, against a 90-second budget
**So that** feedback arrives in about a minute and the full suite waits for the push

## Acceptance Criteria

- **AC1:** Given a change to one script, when the commit's test selection runs, then it selects that script's test module and the modules that import it, and does not add a fixed list of unmeasurable modules
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_a_script_change_selects_its_tests_and_importers
  - **Verified:** yes (2026-09-24)
- **AC2:** Given a commit touching only docs or sdlc-studio artefacts, when the hooks run, then no unit suite runs
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_a_docs_only_commit_runs_no_suite
  - **Verified:** yes (2026-09-24)
- **AC3:** Given selected suites, when they run, then they run in parallel where pytest-xdist is available and the hook reports elapsed time against a 90-second budget, warning rather than refusing when over
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_the_budget_is_reported_not_enforced
  - **Verified:** yes (2026-09-24)
- **AC4:** Given this repository, when test selection answers for a one-script change, then it answers in under 3 seconds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_selection_is_fast_on_this_repository
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
