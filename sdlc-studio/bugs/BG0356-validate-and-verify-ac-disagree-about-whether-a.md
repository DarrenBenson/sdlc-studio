# BG0356: validate and verify_ac disagree about whether a bug's Verify line executes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

validate.py reports a bug's `Verify:` line as pseudo-verify - 'nothing executes this' - while `verify_ac.py` will in fact execute it. Two guards give the author opposite advice about the same line, and a fixed bug consequently has no agreed executable closure path.

## Steps to Reproduce

$ python3 .claude/skills/sdlc-studio/scripts/`verify_ac.py` run --story sdlc-studio/bugs/BG0342-all-four-artefact-indexes-assert-stale-last-updated.md --dry-run --root .
[DRY] BG0342-...: ac=9 pass=9 fail=0 manual=0 unspec; `verify_ac.py`:1569-1574 (`stories = [i for i in ids if i.startswith("US")]`; 'non-story id(s) skipped'); validate.py:185-194 comment plus `if type_ in ("cr", "bug")` pseudo-verify warning. `python3 .claude/skills/sdlc-stu

## Proposed Fix

See the summary; each cited site names its own remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
