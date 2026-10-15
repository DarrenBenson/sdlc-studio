# BG1054: The scheduled corpus-verify lane reads US0892 AC1 red because its job installs no pytest-xdist

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** US1004 round-3 QA verdict (sdlc-studio/reviews/critic-verdicts.md), its [pre-existing] item, reproduced in a venv; scheduled Lint run 38246079155 at b3dcc041.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:40:18Z

## Summary

lint.yml's corpus-verify job installs a shorter package list without pytest-xdist (kept out to protect the baseline comparison, lint.yml:178-180). US0892 AC1's verifier skips without xdist, and `verify_ac` reads an all-skipped verifier as FAIL ('every selected test was SKIPPED'), so the lane reports US0892::AC1 as NEW against a banked baseline of 0. Scheduled run 38246079155 at b3dcc041 (2026-10-12) named it beside US0940::AC1, US0957::AC3 and US0985::AC2, none recorded by an open Bug or CR. The comparison the omission protects is red because of the omission.

## Steps to Reproduce

In a venv holding exactly corpus-verify's install (lint.yml:181), run `verify_ac.py run --id US0892`: AC1 FAIL, every selected test SKIPPED; with pytest-xdist added, 2/2 pass.

## Proposed Fix

Decide the lane's intent and make one reading: either install pytest-xdist in corpus-verify (re-banking the baseline once), or have `verify_ac` read a verifier skipped for a missing optional plugin as UNVERIFIABLE rather than FAIL; then triage US0940::AC1, US0957::AC3 and US0985::AC2 from the same run.

## Acceptance Criteria

- [ ] **AC1** Given the corpus-verify job's own install, when it verifies US0892, then AC1 is not read as a failure caused by a missing plugin.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
