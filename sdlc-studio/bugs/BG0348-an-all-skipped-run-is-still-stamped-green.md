# BG0348: An all-skipped run is still stamped green for unittest, jest, vitest and go

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers); agent; skill v5.0.0

## Summary

BG0317 made an all-skipped PYTEST run not-a-pass. The reviewer verified the same hole survives for every other runner family: a real unittest all-skipped run prints 'Ran 1 test' then 'OK (skipped=1)' and exits 0; jest prints 'Tests: 3 skipped, 3 total'; vitest 'Tests 3 skipped (3)'; a go run of only t.Skip tests prints 'ok pkg'. None matches the zero-count signature `_ran_no_tests` looks for, so each is stamped green by tests that never ran.

## Steps to Reproduce

1. Write a story whose Verify line names an all-skipped unittest selector. 2. Run `verify_ac`: the AC is stamped green. 3. Confirm the runner exits 0 with 'OK (skipped=1)' and no 'no tests ran' text. 4. Repeat for jest, vitest and go using the summary strings above.

## Proposed Fix

Give each runner family its own all-skipped signature beside the pytest one, and make a run whose counts are entirely skipped (plus deselections and warnings) vacuous and not-ok, as the pytest path now is. unittest matters most: it is this repository's own default runner, so the silent pass is live on the path the project itself uses.

## Acceptance Criteria

### AC1: a real all-skipped unittest run is not a pass

- **Given** a module whose only test carries `@unittest.skip`, run through a `shell` verifier
- **When** the verifier exits 0 having printed `Ran 1 test` and `OK (skipped=1)`
- **Then** the result is not ok and is attributed vacuous
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_a_real_all_skipped_unittest_run_is_not_a_pass

### AC2: a mixed unittest run with one skip is still a pass

- **Given** `Ran 4 tests` beside `OK (skipped=1)`, so three tests really ran
- **When** the run is judged
- **Then** it is ok and not vacuous - the check must not turn a normal suite red
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_a_mixed_unittest_run_with_one_skip_is_still_a_pass

### AC3: an all-skipped jest run is not a pass

- **Given** jest's `Tests:       3 skipped, 3 total` summary on a clean exit
- **When** the run is judged
- **Then** it is not ok, and `Tests: 1 skipped, 2 passed, 3 total` still is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_an_all_skipped_jest_run_is_not_a_pass

### AC4: an all-skipped vitest run is not a pass

- **Given** vitest's `Tests  3 skipped (3)` summary on a clean exit
- **When** the run is judged
- **Then** it is not ok, and `Tests  2 passed | 1 skipped (3)` still is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_an_all_skipped_vitest_run_is_not_a_pass

### AC5: a go run whose every test skipped is not a pass

- **Given** `go test -v` output whose only outcome line is `--- SKIP: TestA`, beside `PASS` and `ok pkg`
- **When** the run is judged
- **Then** it is not ok, and a run with one `--- PASS` beside the skip still is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_a_go_run_whose_every_test_skipped_is_not_a_pass

### AC6: the reader is given the skipped remedy, not the re-point one

- **Given** an all-skipped unittest run
- **When** the failure message is composed
- **Then** it says the tests were SKIPPED rather than telling the reader to re-point a selector that is fine
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_the_all_skipped_remedy_is_not_the_re_point_one

### AC7: a green run of every family is untouched

- **Given** an ordinary passing summary from unittest, jest, vitest, go and pytest
- **When** each is judged
- **Then** every one is ok and none is vacuous
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::AllSkippedNonPytestRunnerTests::test_a_green_run_of_every_family_is_untouched

## Notes

Non-verbose `go test` prints `ok pkg 0.002s` whether every test passed or every test called
`t.Skip`, so that one case carries no signal to read and remains undetectable. It is documented
at the signature rather than papered over.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; per-family all-skipped signatures plus regression tests landed |
