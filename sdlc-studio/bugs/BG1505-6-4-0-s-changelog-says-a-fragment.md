# BG1505: 6.4.0's CHANGELOG says a fragment that opens with a list item folds byte for byte, but compose bullets an ordered item, and no test pins a later list item in a prose entry

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** CHANGELOG.md, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, changelog.d/BG1505.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1503 QA verdict 27cc2b82706d-6d2ea24b, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T09:14:25Z

## Summary

BG1503's QA seat (verdict 27cc2b82706d-6d2ea24b) found two gaps. First, the BG1503 entry in CHANGELOG.md's 6.4.0 section says an entry that already opens with a list item folds byte for byte, but `changelog.py compose` folds a fragment opening `1. An ordered first item` as `- 1. An ordered first item`; the docstring and the commit scope the rule to a dash, star or plus item, so only the public sentence over-claims. Second, no test in ComposeBulletTests holds a prose entry whose later lines carry a column-0 list item, so a mutant that searches every line for a list item passes all six bullet tests.

## Steps to Reproduce

1. Write a fragment whose entry opens `1. An ordered first item` and run `changelog.py compose --apply` in a scratch copy: it folds as `- 1. ...`.
2. Mutate `_LIST_ITEM` to re.M with `.search`: `test_changelog.py` still passes.

## Proposed Fix

Say in the CHANGELOG sentence that a dash, star or plus item folds unchanged (or treat an ordered item the same way), and add a bullet test whose prose entry carries a later column-0 list item.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1503's QA seat (verdict 27cc2b82706d-6d2ea24b) found two gaps.
- [ ] **AC2** The proposed fix lands, pinned by a test: Say in the CHANGELOG sentence that a dash, star or plus item folds unchanged (or treat an ordered item the same way), and add a bullet test whose prose entry...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
