# BG0807: The US0942 AC5 stamp test resolves the whole corpus before filtering, costing about 50 seconds of every commit that touches verify_ac.py

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_tag_no_close_owed.py, changelog.d/BG0807.md
> **Severity:** Low
> **Points:** 1

## Summary

CR0592 bullet (file line 48) re-measured at f76b70cc: `test_lean_tag_no_close_owed.py::TagNoCloseOwedTests::test_no_stamp_names_the_retired_flag` took 50 s idle (86 s under load per the filing) against the 90 s commit budget; BG0805's commit pays it.

## Steps to Reproduce

time pytest .claude/skills/sdlc-studio/scripts/tests/`test_lean_tag_no_close_owed.py` -k `test_no_stamp_names_the_retired_flag`

## Proposed Fix

Filter to the artefacts whose Verify lines name US0942's test modules before resolving stamps.

## Acceptance Criteria

- [ ] Given `TagNoCloseOwedTests::test_no_stamp_names_the_retired_flag`, when it runs, then `verify_ac.unresolvable_stamps` is called only on stories and bugs whose Verify lines name a test module US0942's Affects lists, and a stamp naming a deleted node in such a module is still reported. Fails on: resolving every stamp in the corpus and filtering afterwards (HEAD), or filtering so narrowly that the deleted-node mutant survives

## Notes

Land with or before BG0805. Repo-only. Mint from CR0592 and remove the bullet.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0807) |
