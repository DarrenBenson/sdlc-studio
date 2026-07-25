# BG0295: changelog.py compose folds every pending fragment into [Unreleased] and deletes them, with no release gate or confirmation, so a mid-sprint compose prematurely consumes unrelated units' fragments

> **Status:** Open
> **Created:** 2026-07-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py
> **Severity:** Medium
> **Points:** 2

## Summary

compose is the release-time action that folds changelog.d/ fragments into [Unreleased] and consumes (deletes) them. Run at any other time it silently does the same to EVERY pending fragment, not just the caller's - so a routine 'add my one fragment then compose' folds and deletes ~100 other units' fragments, rewriting [Unreleased] and losing the per-unit files the release cut was meant to compose.

## Steps to Reproduce

1. changelog.d/ holds many pending fragments (one per delivered unit awaiting the next release). 2. Add one new fragment. 3. Run changelog.py compose to fold it in. 4. Observe: it composes ALL fragments (observed 116) into [Unreleased] and deletes every fragment file, not only the new one.

## Proposed Fix

Gate compose behind an explicit release intent (a --release flag or a confirmation), or make it refuse when [Unreleased] would be rewritten outside a release cut, so a single-fragment add never consumes the whole pending set. The fragment convention is that fragments accumulate and are composed once, at the release; compose run outside that context should say so rather than act.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-25 | sdlc-studio | Created via `new` (deterministic) |
