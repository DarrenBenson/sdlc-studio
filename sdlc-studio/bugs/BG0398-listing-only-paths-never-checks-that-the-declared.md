# BG0398: listing_only_paths never checks that the declared read IS a listing, and applies one module's declaration globally

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The guard is `rel in paths`, which a CONTENT read satisfies as well as a listing read - the docstring promises the declaration is 'never widened beyond the measurement'. A module that declares a directory and also opens files under it de-relevances the whole tree, and the union means another module's content read of the same directory is silenced too. `.githooks` is a directory-level content read and is not in the protected set.

## Steps to Reproduce

A test module declaring `GATE_LISTING_ONLY`=('docs',) that also reads docs/*.md gives test-relevant: no on a docs edit, while its own assertion fails.

## Proposed Fix

Scope the declaration to the declaring module's own contribution and reject one for a path that module also opens.

## Acceptance Criteria

- [ ] A module that opens files under a directory it declares does not make that directory listing-only.
- [ ] One module's declaration does not silence another module's content read of the same tree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
