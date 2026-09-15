# BG0687: A criterion's second Verify line is recorded but never run, so a both-states requirement cannot be enforced by its selectors

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** BG0667 round-5 plan repair, RUN-01M2JA6J 2026-09-15.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac` reads the first Verify line under a criterion and records any later one without running it. A criterion that must hold in two environments (BG0667 AC5: green with and without `SDLC_STUDIO_BOUNDARY_SUITE`=1) can name both commands, and only the first is ever executed, so the second state is enforced by nobody.

## Steps to Reproduce

1. Give a criterion two Verify lines, the second failing.
2. `verify_ac.py` run --id <unit> reports the criterion pass.

## Proposed Fix

Run every Verify line under a criterion and pass it only when all pass; or refuse a second line at lint time with the reason named.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `verify_ac` reads the first Verify line under a criterion and records any later one without running it.
- [ ] **AC2** The proposed fix lands, pinned by a test: Run every Verify line under a criterion and pass it only when all pass; or refuse a second line at lint time with the reason named.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
