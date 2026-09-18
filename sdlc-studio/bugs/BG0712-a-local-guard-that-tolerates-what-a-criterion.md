# BG0712: a local guard that tolerates what a criterion refuses lets a breach pass the commit and redden CI

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/check_budgets.py, tools/tests/test_check_budgets.py, .githooks/pre-commit
> **Evidence:** RUN-01M2JA6J: commit 578f733d passed pre-commit and reddened main (Lint run 35063958245); the repair d8659180 restored it 1h41m later. The two criteria that caught it are US0096::AC1 and US0473::AC4.
> **Created:** 2026-09-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`check_budgets.py` passes a file up to 5% over its recorded ceiling (`CEILING_TOLERANCE` = 1.05) and the pre-commit hook runs that guard, so a breach commits cleanly. Two criteria then judge the same ceiling WITHOUT the tolerance - US0096 AC1 runs the whole budget test file and US0473 AC4 runs the strict ceiling test by name - and they fail in CI. That is what happened in RUN-01M2JA6J: reference-sprint.md went to 860 lines against a ceiling of 855, committed locally with the guard green, and turned main red, giving the run a 33% change failure rate on three pushes. The class is general: wherever a local guard's tolerance is wider than the criterion that judges the same property, the local gate reports success on a state CI refuses, and the author learns from a red trunk instead of a refusal.

## Steps to Reproduce

1. Add five lines to a reference file at its ceiling. 2. Commit: `check_budgets` reports 'inside the tolerance' and the hook passes. 3. Push: the ci job fails on `test_check_budgets`' two strict criteria.

## Proposed Fix

Make the local guard refuse what CI refuses: the pre-commit lane judges against the ceiling itself, and the tolerance survives only as a REPORT of files inside the band (`--drift` already does exactly that). Where a tolerance must stay, the criteria that judge the same property strictly have to be named in the guard's own refusal, so the difference is visible to whoever is about to commit. Two files sit inside that band today - reference-config.md at 104.89% and reference-review.md at 100.49% - so this refuses immediately and the repair is to raise those ceilings deliberately or shrink the files.

## Acceptance Criteria

The class, not the instance: wherever a local guard tolerates what a criterion refuses, the commit passes and CI fails. The fix is judged on the commit path, because that is where the author is standing when the difference matters.

### AC1: the pre-commit budget lane refuses a file over its ceiling, with no tolerance

- **Given** a fixture skill tree whose `reference-x.md` sits at 103 lines against a recorded ceiling of 100, inside the 1.05 tolerance
- **When** `check_budgets.py --root <fixture>` runs as the pre-commit lane invokes it
- **Then** it exits non-zero and names the file, its lines, its ceiling and the criteria that judge it strictly, so the author sees at commit time what CI would have told them at push time
- **Mutant:** keep `CEILING_TOLERANCE` in the pass/fail decision and report the band - the commit is then green on the exact state that reddened main in RUN-01M2JA6J
- **Verify:** pytest tools/tests/test_check_budgets.py::TolerancePathTests::test_a_file_inside_the_tolerance_is_refused_at_commit_time

### AC2: the tolerance survives as a report, so drift is still visible before it breaches

- **Given** the same fixture, and a second file at 98 lines against a ceiling of 100
- **When** `check_budgets.py --drift --root <fixture>` runs
- **Then** it exits 0 and names every file inside the band with its percentage, the 103-line file included, so a file approaching its ceiling is seen before it crosses
- **Mutant:** delete the drift verb along with the tolerance - the only warning a file is about to breach then disappears, and every breach becomes a surprise
- **Verify:** pytest tools/tests/test_check_budgets.py::TolerancePathTests::test_drift_still_reports_the_band_and_exits_zero

### AC3: the two files inside the band today are resolved deliberately, not by the tolerance

- **Given** this repository, where `reference-config.md` sits at 104.89% of its ceiling and `reference-review.md` at 100.49%
- **When** the strict lane runs on the tree as it stands
- **Then** both are refused, and the delivery either raises each ceiling with a written reason in `check_budgets.py` and the pinned value in the test, or shrinks the file - the choice recorded per file in this bug's Revision History
- **Mutant:** grandfather the two current offenders into an allowlist - the guard then ships strict for everyone except the files that already broke it, which is the ratchet running backwards
- **Verify:** shell python3 tools/check_budgets.py --root . && python3 -m pytest tools/tests/test_check_budgets.py -q

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Filed |
