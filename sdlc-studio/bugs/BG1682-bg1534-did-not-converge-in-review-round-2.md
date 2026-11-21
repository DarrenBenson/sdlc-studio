# BG1682: BG1534 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md, changelog.d/BG1534.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T15:17:46Z

## Summary

BG1534 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's doctest skip (verify\_ac.py:4064, added in 67d57b45) resolves every dotted name, and every name equal to its file's stem, by the file alone, so it reads clean Pass rows pytest cannot run: over a `tests/test_version.py` defining `test_other` and a `RealTests` class carrying a doctest, ts-check at HEAD reports none of `tests/test_version.py::test_version`, `tests/test_version.py::test_version.DeletedTests` and `tests/test_version.py::RealTests.test_real`, each of which `pytest --collect-only --doctest-modules` refuses as `not found`, while the real doctest `tests/test_version.py::test_version.RealTests` collects and a control row `tests/test_version.py::test_gone` is still reported\; the round-1 code (a0131716) reported the first two, so the repair reopens, for a test function named after its own file, the shape AC1 exists to catch, and no test holds a dotted or stem-named id over a missing object as a finding, only the positive doctest rows; RULINGS: Round-1 "Resolution across several files of one name is unpinned" CLOSED: two `test_utils.py` fixtures each defining a different test now resolve both rows and report `test_utils.py::T::test_c` with its other-file count, and the author's any-for-all and first-file-only mutants are killed. Round-1 "The `_TestTree` docstring (verify\_ac.py:4005-4008) says what only a nested checkout defines does not resolve" CLOSED: the docstring now says an explicit path resolves wherever it leads, and rows by explicit path into `.claude/worktrees/other` and `node_modules` read clean while the bare names only they define are reported. Round-1 "A pytest doctest node id is misread as a test" OVER-CLAIMED: the real doctest forms (`file.py::module.name`, `file.py::package.module.name`, `file.py::module`) now read clean, but the fix accepts any dotted or stem-named id without resolving the object it names, the new finding above. AC3 judged by its own shell Verify line in a throwaway clone: it exits 0 on the shipped TS0002, and reverting any one of the four rows (US0052 AC4, US0054 AC1, AC2, AC4) to its base text makes it exit 1 with a finding naming that row, so AC3 holds and its line can fail. AC1-AC3 pass under `verify_ac.py run --id BG1534 --dry-run`. Claim inventory: the commit body's doctest, shared-name, explicit-path and trailing-full-stop claims are TRUE by test and CLI probe, and "resolves them by file alone" is TRUE as written, which is the defect. No regression across the repo's specs: every `sdlc-studio/test-specs/TS*.md` gives the same ts-check result under the base and head verify\_ac.py. Reviewer mutants killed: the module form not skipped, the dotted form not skipped, the regex stopping at the first dot, any single name skipped.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1534 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1534 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's doctest skip (verify\_ac.py:4064, added in 67d57b45) resolves every dotted name, and every name equal to its file's stem, by the file alone, so it reads clean Pass rows pytest cannot run: over a `tests/test_version.py` defining `test_other` and a `RealTests` class carrying a doctest, ts-check at HEAD reports none of `tests/test_version.py::test_version`, `tests/test_version.py::test_version.DeletedTests` and `tests/test_version.py::RealTests.test_real`, each of which `pytest --collect-only --doctest-modules` refuses as `not found`, while the real doctest `tests/test_version.py::test_version.RealTests` collects and a control row `tests/test_version.py::test_gone` is still reported; the round-1 code (a0131716) reported the first two, so the repair reopens, for a test function named after its own file, the shape AC1 exists to catch, and no test holds a dotted or stem-named id over a missing object as a finding, only the positive doctest rows
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1534 AC1 still passes: Given a test spec whose AC Coverage Matrix marks a row Pass and whose Test Cases cell names a test file and test title that nothing in the tree defines, when `verify_ac.py ts-check --spec` reads it, then the check reports a finding naming that row and does not print `ts-check: 0 finding(s)`. Fails on: a Pass row over a test nobody can run reading as clean.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TsCheckSelectorResolutionTests::test_a_pass_row_naming_a_missing_test_is_a_finding
- [ ] **AC3** BG1534 AC2 still passes: Given the same spec with one Pass row naming a test that exists in the tree and one whose Test Cases cell names no test file (a manual check), when `ts-check` reads it, then neither row is reported. Fails on: a finding against a resolvable row, or against a cell that names no file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TsCheckSelectorResolutionTests::test_a_resolvable_row_and_a_manual_row_are_not_findings
- [ ] **AC4** BG1534 AC3 still passes: Given `sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md` after the fix, when `ts-check --spec` reads it with the new resolution, then it reports no finding: the rows for US0052 AC4 and US0054 AC1, AC2 and AC4 match the stories' manual Verify lines after US0921 and the spec no longer describes a gate mutation lane as live. Fails on: a row still naming `MutationLaneTests` or `test_runner_error_not_a_kill`.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py ts-check --spec sdlc-studio/test-specs/TS0002-mutation-check-gate-test-spec.md | grep -q 'ts-check: 0 finding(s)'

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
