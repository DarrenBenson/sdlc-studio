# BG1211: The shell-hazard check flags unittest's own assertion separator ('X is not None : msg') when a reviewer's finding quoting it is carried into a bug

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py, changelog.d/BG1211.md
> **Evidence:** Push gate at cc758984 on devserver1, boundary-suite-last.log; BG1205's summary and AC2.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T16:34:39Z

## Summary

2026-11-04, the push gate at cc758984 (run five). critic's carry at the review cap filed BG1205 with a reviewer's finding quoting a unittest failure, '400 is not None : a Claude legacy baseline ...'. `test_shell_hazard_rate.py`::MeasuredCatchRateTests::`test_no_legitimate_artefact_field_is_flagged` then failed: the hazard fingerprint read the space before the colon as what a completed command substitution removed. The quote was re-spaced by hand to clear the gate. unittest writes 'first is not second : msg' for every assertIsNone/assertIs failure, so any carried or filed finding quoting one trips the same false positive.

## Steps to Reproduce

1. File a finding whose summary contains `400 is not None : a reason`.
2. Run `test_shell_hazard_rate.py`::MeasuredCatchRateTests::`test_no_legitimate_artefact_field_is_flagged`: it fails on that field.

## Proposed Fix

Exempt unittest's ` : ` message separator after an assertion's operands from the space-before-punctuation fingerprint, or quote carried findings in a code span the check skips.

## Acceptance Criteria

- [ ] **AC1** A field quoting `400 is not None : a reason` is not flagged, and the measured catch rate holds.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py

## Impact

Every carry or finding that quotes a unittest failure turns the push gate red on a legitimate field.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
