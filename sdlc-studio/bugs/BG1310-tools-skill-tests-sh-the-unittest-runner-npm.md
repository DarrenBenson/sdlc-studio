# BG1310: `tools/skill-tests.sh`, the unittest runner `npm test` uses, loads no conftest, so the harness-variable scrub BG1197 added never runs there and the meter tests fail under a Cursor session

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/skill-tests.sh, conftest.py, tools/tests/test_skill_tests_env.py
> **Evidence:** The run nine US0986 builder's hand-back (2026-11-09): the CURSOR_AGENT=1 and CLAUDECODE=1 runs of the 14 modules through tools/skill-tests.sh
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:40:54Z

## Summary

Found rebuilding US0986 with BG1205 in run nine (2026-11-09). BG1197's root conftest.py clears the harness variables before any meter test runs, so under pytest the suite no longer depends on the harness running it (382 passed; 88 failed with `--noconftest`). `tools/skill-tests.sh` runs the skill's tests through unittest, which loads no conftest, so the scrub never runs: with `CURSOR_AGENT`=1 set, the 14 meter-reaching modules other than `test_token_meters.py` and `test_meter_cursor.py` give 74 failures and 14 errors, and pass with CLAUDECODE=1. A contributor running `npm test` from a Cursor, Copilot or OpenCode session sees a red suite that the push gate (pytest) shows green.

## Steps to Reproduce

1. Export `CURSOR_AGENT`=1 in a shell.
2. Run `bash tools/skill-tests.sh`.
3. The meter-reaching modules fail (74 failures, 14 errors); the same run with CLAUDECODE=1 passes.

## Proposed Fix

Have the unittest runner apply the same harness-variable scrub the conftest applies before it loads any test module (one shared helper both call), and add a test that runs one meter-reaching module through the runner with `CURSOR_AGENT` set and sees it pass.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Found rebuilding US0986 with BG1205 in run nine (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Have the unittest runner apply the same harness-variable scrub the conftest applies before it loads any test module (one shared helper both call), and add a...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
