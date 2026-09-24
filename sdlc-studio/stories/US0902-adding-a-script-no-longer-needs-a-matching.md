# US0902: Adding a script no longer needs a matching TSD sentence to commit

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_script_tests.py, tools/tests/test_check_script_tests.py, .githooks/pre-commit, package.json, AGENTS.md, sdlc-studio/tsd.md, tools/tests/test_precommit_lane_order.py, tools/tests/test_lean_tsd_script_pin.py, tools/tests/test_message_first_gate.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** developer adding a script
**I want** the script-tests lane, which pins the TSD's prose map to the scripts tree, deleted
**So that** a new script lands with its tests, and nobody has to edit a document list to satisfy a lane that catches no code defect

## Acceptance Criteria

- **AC1:** Given a new script under `scripts/` with no entry in the TSD's unit coverage map, when a commit and `npm run lint` run, then neither refuses: the script-tests lane, tools/`check_script_tests.py` and its test module are deleted, and the TSD no longer says a checker holds its map to the tree
  - **Verify:** pytest tools/tests/test_lean_tsd_script_pin.py::ScriptTestsLaneTests::test_an_unmapped_script_refuses_no_commit
  - **Verified:** yes (2026-09-24)
- **AC2:** Given the test nodes this story deletes, then the six stamped criteria naming `test_check_script_tests` nodes, across three artefacts, are retired in the D0259 pattern (`Verify: manual - retired by <this story>: <why>`, `Verified: manual (<date>) - retired, superseded by <this story>`), so `verify_ac.py stamps --staged` passes on the deleting commit
  - **Verify:** pytest tools/tests/test_lean_tsd_script_pin.py::ScriptTestsLaneTests::test_the_script_tests_criteria_are_retired
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-24 | Claude Opus 5.5 | AC2's count corrected in delivery: five stamped criteria on US0456 plus one unstamped on BG0727, across two artefacts, not six across three |
