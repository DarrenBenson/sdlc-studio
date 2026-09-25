# BG0776: sprint sign --principal - seals the run with an empty principal

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sign.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:11:16Z

## Summary

sprint.py sign refuses an empty --principal, but the guard strips the raw string before sprint's id normaliser reads '-' as empty, so '--principal -' passes the guard and seals the run under an empty principal. An alias such as 'Sam (qa-seat)' is also not matched to recorded reviewer qa-seat. Pre-existing (identical at base); found by US0919's round-2 QA review.

## Steps to Reproduce

1. In a closed run fixture, python3 sprint.py sign --report RPT0001 --principal -. 2. It exits 0 and the run is sealed; the signature names no principal.

## Proposed Fix

Normalise the principal before the empty check, and refuse a value that normalises to empty; pin it with a test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: sprint.py sign refuses an empty --principal, but the guard strips the raw string before sprint's id normaliser reads '-' as empty, so '--principal -' passes...
- [ ] **AC2** The proposed fix lands, pinned by a test: Normalise the principal before the empty check, and refuse a value that normalises to empty; pin it with a test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
