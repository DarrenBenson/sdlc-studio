# US0901: The hooks list their own lanes, and AGENTS.md stops restating them

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** AGENTS.md, .githooks/pre-commit, .githooks/commit-msg, tools/boundary_roster.py, tools/tests/test_lean_commit_lanes.py, tools/tests/test_boundary_roster.py, tools/tests/test_check_spec_claims.py, tools/tests/test_precommit_lane_order.py
> **Epic:** EP0262
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** developer or agent starting a session
**I want** to ask each hook which lanes it runs, instead of reading a roster in AGENTS.md that tests hold to the hooks
**So that** AGENTS.md shrinks back towards a page that gets read, and changing a lane no longer means editing prose and four prose-pinning tests

## Acceptance Criteria

- **AC1:** Given `.githooks/pre-commit --list` and `.githooks/commit-msg --list`, then each prints every lane it runs, one per line with its key and the rule it enforces, runs none of them (the hook fixture's tripwires stay silent) and exits 0; a lane added to a hook appears in its list with no other file edited
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneListTests::test_each_hook_lists_its_lanes_without_running_them
- **AC2:** Given AGENTS.md, then it carries no lane roster and points at the two `--list` commands; the tests that pinned its prose (the roster half of `test_lean_commit_lanes`, GateLaneTests and StampsStagedRosterTests in `test_check_spec_claims`, `ChangelogShapeLaneTests::test_the_agents_roster_names_the_lane`, `test_boundary_roster)` and tools/`boundary_roster.py` are deleted, so no test reads AGENTS.md to pin a lane or boundary name
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneListTests::test_agents_md_points_at_the_lists_and_no_test_pins_its_prose
- **AC3:** Given the test nodes this story deletes, then every stamped criterion naming one is retired in the D0259 pattern (`Verify: manual - retired by <this story>: <why>`, `Verified: manual (<date>) - retired, superseded by <this story>`), and US0879's revision history records that AC1's roster clause is superseded by this story, so `verify_ac.py stamps --staged` passes on the deleting commit
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneListTests::test_the_roster_criteria_are_retired

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
