# BG1485: A shell Verify line run with -s still reads all-skipped and no-tests shapes from its whole output, and a partial-skip test's docstring still says the release gate counts the skips

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py, .claude/skills/sdlc-studio/scripts/tests/test_partial_skip_release_gate_count.py, changelog.d/BG1485.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Run fourteen fixes lane builder hand-back (BG1478, BG1480, BG1479, BG1484), 2026-11-15.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T22:25:20Z

## Summary

Left by the run fourteen fixes lane, outside its criteria. (1) BG1479 made a `pytest` Verify line read its all-skipped and no-tests verdicts from pytest's closing summary line only, but a `shell` Verify line that runs pytest with -s still searches its whole output, so a test printing '1 skipped in 0.01s' reads as all-skipped there. (2) `test_partial_skip_release_gate_count.py`'s module docstring says 'The release gate counts its partial skips', the overclaim BG1479 removed from BG1395's fragment: gate.py --release never reads `partly_skipped.`

## Steps to Reproduce

1. A shell Verify line `python3 -m pytest <file> -s` whose test prints '1 skipped in 0.01s' and passes reads as all-skipped.
2. Read the module docstring of `test_partial_skip_release_gate_count.py.`

## Proposed Fix

Apply the closing-summary read to a shell line whose command runs pytest, and correct the docstring to say `verify_ac` prints and records the count.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Left by the run fourteen fixes lane, outside its criteria.
- [ ] **AC2** The proposed fix lands, pinned by a test: Apply the closing-summary read to a shell line whose command runs pytest, and correct the docstring to say `verify_ac` prints and records the count.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
