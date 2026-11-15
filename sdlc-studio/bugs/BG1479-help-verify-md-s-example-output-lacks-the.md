# BG1479: help/verify.md's example output lacks the unspecified= and partly_skipped= fields verify_ac prints, and the all-skipped check reads test output under -s

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py, changelog.d/BG1479.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Run fourteen, the verify lane's builder hand-back (BG1396, BG1395), 2026-11-15.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:47:20Z

## Summary

Two gaps found by BG1395 and BG1396's builder, outside their Affects. (1) help/verify.md's example `run` and `report` output (near lines 82-205) predates `unspecified=` and now also lacks `partly_skipped=` and the new `total:` line, so the page shows output the tool no longer prints. (2) `verify_ac.py`'s all-skipped check still searches the whole captured output, so under `-s` a test that prints a bare line like '1 skipped in 0.01s' is read as an all-skipped run, though the partial-skip read now uses pytest's final summary only.

## Steps to Reproduce

1. Compare help/verify.md's example output with `verify_ac.py run --id <id> --dry-run`.
2. Run a Verify line with -s whose test prints '1 skipped in 0.01s': it reads as all-skipped.

## Proposed Fix

Regenerate the help page's examples from the tool's real output, and read the all-skipped verdict from pytest's final summary line as the partial-skip read does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Two gaps found by BG1395 and BG1396's builder, outside their Affects.
- [ ] **AC2** The proposed fix lands, pinned by a test: Regenerate the help page's examples from the tool's real output, and read the all-skipped verdict from pytest's final summary line as the partial-skip read...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
