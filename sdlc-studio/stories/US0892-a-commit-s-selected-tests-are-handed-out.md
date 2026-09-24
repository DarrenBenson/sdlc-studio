# US0892: A commit's selected tests are handed out one at a time across every worker

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change to a hub script
**I want** the commit's selected tests to be handed out one at a time across the xdist workers
**So that** workers stop idling at 21% busy while one of them works through a run of heavy tests, saving 28-40s on a hub commit

## Acceptance Criteria

- **AC1:** Given a commit's selection with pytest-xdist present, when `gate.run_tests_plan` builds the commit's commands, then the parallel command hands tests out one at a time (`--maxschedchunk=1`) so no worker is given a run of consecutive heavy tests up front, and the `serial_only` phase is unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SchedulingTests::test_the_parallel_phase_hands_out_one_test_at_a_time
- **AC2:** Given the descriptor-and-temp-file leak check in `test_mutation.py` (`TheRunLeavesNothingBehindTests::test_a_construction_failure_leaks_no_descriptor_and_no_temp_file`) running while another process creates `mutation_run_*` files in the shared temp directory, then it passes: it counts only a temp directory private to itself, or runs in the `serial_only` phase (with chunk 1 it failed 2 of 12 runs)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SchedulingTests::test_a_sibling_temp_file_cannot_redden_the_leak_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
