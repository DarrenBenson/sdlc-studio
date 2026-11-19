# BG1534: TS0002 marks four matrix rows Pass against tests that no longer exist, and ts-check reports no finding

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md, changelog.d/BG1534.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, tsd lens, survived 3 of 3 refute votes; observed at sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md AC Coverage Matrix, rows US0052 AC4 and US0054 AC1, AC2, AC4; the checker is `ts_check` in .claude/skills/sdlc-studio/scripts/verify_ac.py lines 3853-3925
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:31Z

## Summary

The AC Coverage Matrix of `sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md` marks every row Pass. Three rows (US0054 AC1, AC2 and AC4) name tests in a `MutationLaneTests` class that was deleted when the gate's mutation lane was retired under US0921, and a fourth (US0052 AC4) names `test_runner_error_not_a_kill`, which no test file defines. The stories were repointed to a manual Verify line but the spec was not, and its Status is still Complete. The spec's own validator cannot fail on this: `ts_check` in `verify_ac.py` (lines 3853 to 3925) checks only that the Test Cases cell is non-empty and the Status cell is a pass word, and never resolves the selector. A matrix row can therefore claim Pass over a test nobody can run, which is the decorative matrix the check exists to prevent.

## Steps to Reproduce

1. Open `sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md` and read matrix lines 37, 45, 46 and 47: each names a test and is marked Pass.
2. Search `.claude/skills/sdlc-studio/scripts/tests` and `tools/tests` for `MutationLaneTests` and `test_runner_error_not_a_kill`: there is no match.
3. Run `verify_ac.py` with the `ts-check` subcommand and `--spec` pointing at the TS0002 file.
4. Observe the output 'ts-check: 0 finding(s)' and exit status 0.
5. Expected: the check reports each row whose named test cannot be found. Actual: it passes a spec with four rows naming tests that do not exist.

## Proposed Fix

Extend `ts_check` in `verify_ac.py` so that a matrix row marked with a pass word whose Test Cases cell names a test file and test title is resolved against the tree, and a row whose file or title does not exist is reported as a finding naming the row. Add tests to `test_verify_ac.py` for a row naming a missing test (finding) beside a row naming a real one (no finding). Then correct TS0002: repoint or retire the four rows to match the stories' manual Verify lines after US0921, and reword the parts of the spec that describe a gate mutation lane which no longer exists.

## Acceptance Criteria

- [ ] **AC1** Given a test spec whose AC Coverage Matrix marks a row Pass and whose Test Cases cell names a test file and test title that nothing in the tree defines, when `verify_ac.py ts-check --spec` reads it, then the check reports a finding naming that row and does not print `ts-check: 0 finding(s)`. Fails on: a Pass row over a test nobody can run reading as clean.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TsCheckSelectorResolutionTests::test_a_pass_row_naming_a_missing_test_is_a_finding
- [ ] **AC2** Given the same spec with one Pass row naming a test that exists in the tree and one whose Test Cases cell names no test file (a manual check), when `ts-check` reads it, then neither row is reported. Fails on: a finding against a resolvable row, or against a cell that names no file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TsCheckSelectorResolutionTests::test_a_resolvable_row_and_a_manual_row_are_not_findings
- [ ] **AC3** Given `sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md` after the fix, when `ts-check --spec` reads it with the new resolution, then it reports no finding: the rows for US0052 AC4 and US0054 AC1, AC2 and AC4 match the stories' manual Verify lines after US0921 and the spec no longer describes a gate mutation lane as live. Fails on: a row still naming `MutationLaneTests` or `test_runner_error_not_a_kill`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
