# BG0229: verify_ac ts-check reads a missing spec as an empty one and reports a clean matrix, so a typo'd --spec passes as green

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

`ts_check` reads a non-existent spec file as empty text and then reports a clean AC Coverage Matrix with exit 0. A gate pointed at a moved, renamed or typo'd spec path therefore reports 'every AC is mapped to a passing test case' when it read nothing at all. This is the vacuous-pass family of BG0197 and BG0131: a checker that passes on input it cannot parse reports coverage it does not have, and ts-check exists precisely to stop the AC-to-test matrix being decorative. Found while fixing BG0220 - one draft test there passed for exactly this reason (asserting rc 0 while the spec was never found), which is how it surfaced.

## Steps to Reproduce

Run `verify_ac.py` ts-check --spec sdlc-studio/test-specs/DOES-NOT-EXIST.md. Observed: a clean matrix and exit 0. Expected: a refusal naming the unreadable path, distinct from 'the matrix is complete'.

## Proposed Fix

Refuse an unreadable or absent spec loudly with a non-zero exit, naming the resolved path that was tried. 'Absent' and 'empty but present' are different facts and must not share an exit code. Pin it with a test that asserts the non-zero exit on a missing path, since a test asserting rc 0 is satisfied by the defect itself.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
