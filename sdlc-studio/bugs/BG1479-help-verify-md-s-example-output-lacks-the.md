# BG1479: help/verify.md's example output lacks the unspecified= and partly_skipped= fields verify_ac prints, and the all-skipped check reads test output under -s

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_help_example.py, changelog.d/BG1395.md, changelog.d/BG1396.md, changelog.d/BG1479.md
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

- [ ] **AC1** Given a pytest Verify line run with `-s` whose test prints a bare `1 skipped in 0.01s` line (and, separately, a `no tests ran in` line) and then passes, when `verify_ac.py run` runs that criterion, then it passes: the all-skipped verdict is read from pytest's final summary line only, as the partial-skip read is. Fails on: a printed summary-shaped line read as an all-skipped run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_flag_skip_read.py
- [ ] **AC2** Given help/verify.md, when its example `run` and `report` output is compared with what `verify_ac.py` prints for the same fixture, then each example story line carries the `unspecified=` and `partly_skipped=` fields and the `run` example carries the `total:` line. Fails on: an example line missing a field the tool prints.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_help_example.py
- [ ] **AC3** Given changelog.d/BG1395.md and changelog.d/BG1396.md, when each is read against the code, then neither claims what the code does not do: BG1395's says the count is printed and recorded by `verify_ac.py` and makes no claim that `gate.py --release` reads it, and BG1396's claim about summary-shaped lines under `-s` is true once AC1 holds. Fails on: either fragment naming a reader or a case the code does not serve.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
