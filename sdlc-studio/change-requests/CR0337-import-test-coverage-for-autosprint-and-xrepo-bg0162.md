# CR-0337: Import/test coverage for autosprint and xrepo (BG0162 rider)

> **Status:** Deferred
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/autosprint.py, .claude/skills/sdlc-studio/scripts/lib/xrepo.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0162 corrected the TSD to state that autosprint and lib/xrepo are untested. The coverage gap remains: add real test files or a CI import sweep.

## Impact

Two shipped scripts (autosprint, lib/xrepo) have no test coverage; a regression in either ships undetected by the suite.

## Acceptance Criteria

- [ ] `test_autosprint.py` and `test_xrepo.py` exist and exercise the primary path of each, OR a CI import-coverage sweep names them; the TSD coverage note is updated to match.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
