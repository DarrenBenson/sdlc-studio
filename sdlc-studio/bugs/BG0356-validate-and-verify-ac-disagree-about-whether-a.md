# BG0356: validate and verify_ac disagree about whether a bug's Verify line executes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

validate.py reports a bug's Verify: line as pseudo-verify - 'nothing executes this' - while verify_ac.py will in fact execute it. Two guards give the author opposite advice about the same line, and a fixed bug consequently has no agreed executable closure path.

## Steps to Reproduce

Run verify_ac in dry-run over a bug artefact whose acceptance criteria carry pytest Verify lines. It reports nine criteria, nine passing, none unspecified - so verify_ac does execute them. Then run validate check over the same file: it reports each of those lines as pseudo-verify, meaning nothing executes it. Two shipped guards give the author opposite advice about the same line. The verify_ac side skips only ids that do not begin with the story prefix; the validate side warns for any artefact typed change-request or bug.

## Proposed Fix

See the summary; each cited site names its own remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
