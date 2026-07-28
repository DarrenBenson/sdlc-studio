# BG0386: caller-check --unit is single-valued, so a repeated flag silently checks only the last unit and reports a clean batch

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** critic.py:2231 add_argument("--unit", required=True) - no action=append; the caller-check parser is the same shape
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`caller-check` declares `--unit` with `add_argument("--unit", required=True)` and no `action="append"`, so `--unit US0542 --unit US0543` keeps only `US0543` and argparse says nothing. The command reports on ONE unit while the caller believes it reported on the batch, and a clean result reads as a clean batch.

This has already produced a false measurement in this repository. During RUN-01KYKVZM a caller-check invoked with repeated `--unit` flags returned one finding; that was recorded as `caller-unnamed 5 -> 0` in a retro and in two commit messages before the library call was checked and showed 17 of 23. The invocation was the defect, not the code under test.

## Steps to Reproduce

1. `python3 critic.py caller-check --unit US0542 --unit US0543 --root .`
2. One finding is printed, for US0543 only. US0542 also has a finding when checked alone.
3. `python3 critic.py caller-check --unit US0542 --root .` -> a finding. The batch form hid it.

## Proposed Fix

Accept the batch: `--unit` repeatable (`action='append'`), plus a `--units` comma-separated form and `--from-run` for the open batch, matching how `verify_ac` scopes. Print the unit COUNT checked alongside the findings, so a caller can see the scope the answer covers rather than infer it.

## Acceptance Criteria

- [ ] A repeated `--unit` flag checks every named unit, pinned by a test asserting two units with findings both appear.
- [ ] The command states how many units it checked, so a clean result names the scope it is clean over.
- [ ] A batch form exists that takes the open run's units without naming them by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
