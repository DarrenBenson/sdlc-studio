# US0605: verify_ac lane-check reports criteria whose verifiers never enter the shipped entry point, for units whose Affects names a CLI-bearing script

> **Status:** Ready
> **Delivers:** CR0520
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0199
> **Points:** 5

## User Story

**As a** reviewer asked to confirm a feature works
**I want** criteria verified only through the library reported as such
**So that** a green test cannot stand in for a feature whose lane was never wired

## Acceptance Criteria

### AC1: a library-only verifier is reported

- **Given** a unit whose Affects names a CLI-bearing script and whose criteria are verified only by tests that import the module
- **When** `verify_ac.py lane-check` runs
- **Then** those criteria are reported, because the wiring between entry point and function is the part a library test does not exercise
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_a_library_only_verifier_is_reported

### AC2: a criterion verified through the CLI is reported clean

- **Given** a unit whose criteria invoke the shipped entry point
- **When** the same pass runs
- **Then** it reports nothing, so the check discriminates rather than flagging every unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_a_cli_verifier_is_clean

### AC3: detection is by execution over the verifier's source, not by naming convention

- **Given** a test whose name suggests a CLI test but which never calls `main()` or invokes the script
- **When** the pass runs
- **Then** it is reported, because a convention is satisfied by a rename and this must not be
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_detection_is_by_execution_not_by_name

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
