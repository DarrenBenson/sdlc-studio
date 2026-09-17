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

- [ ] **AC1** The behaviour described is corrected: `check_budgets.py` passes a file up to 5% over its recorded ceiling (`CEILING_TOLERANCE` = 1.05) and the pre-commit hook runs that guard, so a breach commits...
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the local guard refuse what CI refuses: the pre-commit lane judges against the ceiling itself, and the tolerance survives only as a REPORT of files inside...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Filed |
