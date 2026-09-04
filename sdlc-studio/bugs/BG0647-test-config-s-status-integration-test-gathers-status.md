# BG0647: test_config's status integration test gathers status over the REAL repository, so the suite's duration and its noise count depend on this tree's state

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`IntegrationTests.test_status_reads_config` in `test_config.py` calls status.gather(Path('.')) over whatever repository the suite runs in. On this corpus that is 72 to 113 seconds in one test, and every diagnostic the real tree makes status print - on 2026-09-04, twelve 'closure with no separator' warnings from the repair ledger while a run is open - lands in the green-run noise count, which is how a full local run reads 118 against a baseline of 106 while nothing in the diff leaks. The count therefore differs between a clone with an open run and CI, which has no .local state. Found bisecting the noise gate during BG0643's delivery.

## Steps to Reproduce

1. PYTHONPATH=.claude/skills/sdlc-studio/scripts/tests python3 -m unittest `test_config.IntegrationTests.test_status_reads_config` 2>&1 | python3 tools/`test_noise.py` --baseline 0. 2. Observe about 72 s and the closure warnings counted as leaks.

## Proposed Fix

Point the test at a fixture workspace that carries a config-defaults.yaml (the claim is that status consumes the config, which a two-artefact fixture proves in under a second), and capture its output. Keep one smoke over the real tree only where a criterion needs it, and never inside the noise-gated suite.

## Acceptance Criteria

- [x] **AC1** Given a fixture workspace with no config of its own (its directories are inert - `status` reads the defaults for any root), when `test_status_reads_config` runs, then it gathers that fixture with its console captured, reads `schema_version` 2 from the defaults, sees NO open run (this clone has one, so the pin is timing-independent), reads an override of 3 back from a fixture that carries one (so the config is consumed, not defaulted by accident), and completes in under two seconds - never this repository
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::IntegrationTests::test_status_gathers_a_fixture_never_this_repository
  - **Verified:** yes (2026-09-04)
- [x] **AC2** Given the same fixture, when status gathers it, then nothing reaches stdout or stderr - the module's noise count no longer depends on the state of the repository the suite runs in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::IntegrationTests::test_the_status_gather_prints_nothing_for_a_fixture
  - **Verified:** yes (2026-09-04)
- [x] **AC3** Given a fixture whose `.config.yaml` cannot be honoured, when status gathers it, then the warning it prints is in the captured text and nothing reaches the runner's console - "captured" pinned separately from "silent". Added at plan review on 2026-09-04
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::IntegrationTests::test_a_noisy_fixture_is_captured_and_never_reaches_the_console
  - **Verified:** yes (2026-09-04)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/tests/test_config.py`, gather `Path(".")` again - today's code - so the test reads this repository and takes over two seconds | Given a fixture workspace with no config of its own (its directories are inert - `status` reads the defaults for any root), when `test_status_reads_config` runs, then it gathers that fixture with its console captured, reads `schema_version` 2 from the defaults, sees NO open run (this clone has one, so the pin is timing-independent), reads an override of 3 back from a fixture that carries one (so the config is consumed, not defaulted by accident), and completes in under two seconds - never this repository |
| AC1 | in `.claude/skills/sdlc-studio/scripts/status.py`, return None for `schema_version` so the defaults are never consulted - the row the plan review asked for in place of an equivalent one | Given a fixture workspace with no config of its own (its directories are inert - `status` reads the defaults for any root), when `test_status_reads_config` runs, then it gathers that fixture with its console captured, reads `schema_version` 2 from the defaults, sees NO open run (this clone has one, so the pin is timing-independent), reads an override of 3 back from a fixture that carries one (so the config is consumed, not defaulted by accident), and completes in under two seconds - never this repository |
| AC2 | in `.claude/skills/sdlc-studio/scripts/status.py`, print a line at the top of `gather` so a fixture gather reaches the console | Given the same fixture, when status gathers it, then nothing reaches stdout or stderr - the module's noise count no longer depends on the state of the repository the suite runs in |
| AC3 | in `.claude/skills/sdlc-studio/scripts/tests/test_config.py`, remove the stdout and stderr redirect around the noisy gather, so the warning reaches the runner's console and the captured text is empty | Given a fixture whose `.config.yaml` cannot be honoured, when status gathers it, then the warning it prints is in the captured text and nothing reaches the runner's console - "captured" pinned separately from "silent". Added at plan review on 2026-09-04 |
| AC3 | in `.claude/skills/sdlc-studio/scripts/config.py`, route the loader's `could not load` warning to `sys.__stderr__` past any redirect, so one of the two warning sites leaks to the runner's console while the other is captured (delivery review, engineering seat) | Given a fixture whose `.config.yaml` cannot be honoured, when status gathers it, then the warning it prints is in the captured text and nothing reaches the runner's console - "captured" pinned separately from "silent". Added at plan review on 2026-09-04 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
| 2026-09-04 | sdlc | Plan review (two rounds, 2026-09-04): AC3 added to pin 'captured' separately from 'silent'; AC1 row 2 replaced with the run-is-None pin after a timing-only assertion was rejected |
| 2026-09-04 | sdlc | Delivery review r1 (engineering REJECT): AC3's test now re-imports the loader and asserts BOTH warning sites in the captured text; the seat's mutant (route the loader warning to `sys.__stderr__`) added as an AC3 plan row and killed; five mutants re-measured in one pass after the edit |
