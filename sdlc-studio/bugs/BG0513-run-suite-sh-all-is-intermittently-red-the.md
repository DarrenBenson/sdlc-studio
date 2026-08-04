# BG0513: run-suite.sh all is intermittently red: the tools suite takes 4.5x longer inside the full runner than alone, and one test fails when it does

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.py
> **Evidence:** Observed across five full-runner invocations on 2026-08-04 while delivering US0487: GREEN at 577s, RED at 1159s, RED at 1143s, against trees differing only by a regenerated charter index and three lines of reference-schema.md. The first slow run was caused by the author running two suites concurrently; the later two were not, so contention does not account for them.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`tools/run-suite.sh all` returned GREEN (5930 passed, 577s) and then RED twice (1159s and 1143s) over trees that differ only by a regenerated index and a schema-doc addition. In each red run the tools leg reports `Ran 680 tests in ~721s` and `FAILED (failures=1, skipped=2)`; in the green run, and every standalone run, the same 680 tests take ~159s and pass. Both suites pass in isolation: `pytest tools/tests` 678 passed, `python3 -m unittest discover -s tools/tests` exits 0 with 680 tests OK, `pytest scripts/tests` 5930 passed. So the failure is not in either suite's content - it appears only when the tools leg runs about four and a half times slower than it does alone, which happens only inside the full runner. The runner's own gate-budget lane sees it and says so: `OVER - 626s of a 380s budget, +97%`. It is a FAILURE rather than an ERROR, so it is an assertion that stopped holding, not a subprocess timeout expiring. The failing test's name was not captured: the runner's saved log (`sdlc-studio/.local/gate-suite-last.log`) holds a different run by the time the red result is read, and the streamed output carries the `FAILED (failures=1)` summary without the `FAIL:` header line that names the test.

## Steps to Reproduce

1. `bash tools/run-suite.sh all` - note the duration and the verdict.
2. Repeat until a run exceeds about 1100s; it reports RED with the tools leg at ~721s and `failures=1`.
3. `python3 -B -m unittest discover -s tools/tests -t . -q` alone - 680 tests, exit 0, ~159s.
4. `python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests -q` alone - 5930 passed, exit 0.

## Proposed Fix

First make the failure NAMEABLE, which is the part currently missing: the runner must preserve the failing leg's full output for the run whose verdict it just wrote, rather than a log a later run overwrites. Then find what makes the tools leg four and a half times slower inside the runner than outside it - the skill leg runs first and takes about 404s, so shared state it leaves behind is the first place to look - and either isolate it or pin the assertion that depends on it.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `tools/run-suite.sh all` returned GREEN (5930 passed, 577s) and then RED twice (1159s and 1143s) over trees that differ only by a regenerated index and a...
- [ ] The proposed fix lands, pinned by a test: First make the failure NAMEABLE, which is the part currently missing: the runner must preserve the failing leg's full output for the run whose verdict it just...

## Impact

This blocks every commit that touches shared surface, because the suite-claim lane checks a message's green claim against the recorded verdict. It also makes the verdict itself untrustworthy in the direction that matters least often but costs most: a red that is not about the code teaches an author to re-run until it passes, which is how a real red gets waved through.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
