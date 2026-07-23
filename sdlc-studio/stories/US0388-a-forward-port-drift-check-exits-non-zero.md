# US0388: a forward-port drift check exits non-zero with a differing-file count, handling no copy and a pinned copy

> **Status:** Draft
> **Delivers:** CR0389
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0144
> **Points:** 3
> **Affects:** tools/forward-port.sh, tools/tests/test_forward_port.py, AGENTS.md

## User Story

**As an** operator whose other projects load the installed skill copy
**I want** a check that says the installed copy has drifted from the repository tree, and by how many files
**So that** the window between a fix landing here and the mirror running is visible rather than resting on someone remembering to ask

## Acceptance Criteria

### AC1: A drifted target exits non-zero and names the count

- **Given** a target directory whose skill tree differs from the repository tree in a known number of files
- **When** `tools/forward-port.sh --check --target <dir>` runs
- **Then** it exits non-zero and prints the count of differing files as well as the itemised list, and it writes nothing to the target
- **Verify:** pytest tools/tests/test_forward_port.py::DriftCheckTests::test_check_exits_non_zero_and_names_the_differing_file_count

### AC2: An identical target is in sync, and local state is not drift

- **Given** a target that matches the repository tree but carries its own `.local/` state and bytecode or test caches
- **When** the check runs
- **Then** it exits zero and reports the copy as in sync, because the comparison honours the same exclusions the mirror does
- **Verify:** pytest tools/tests/test_forward_port.py::DriftCheckTests::test_an_identical_target_is_in_sync_and_local_state_is_not_drift

### AC3: No installed copy, or a pinned one, is reported rather than failed

- **Given** a machine with no installed copy at the target path, or one carrying the pin marker under its `.local/`
- **When** the check runs
- **Then** it exits zero and says which of the two states it found, so a machine that deliberately does not mirror is not held to a drift verdict
- **Verify:** pytest tools/tests/test_forward_port.py::DriftCheckTests::test_an_absent_or_pinned_copy_is_reported_and_does_not_fail

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built TDD: `forward-port.sh --check` (file-level count, absent/pinned reported); 3 ACs green, mutation-proven |
