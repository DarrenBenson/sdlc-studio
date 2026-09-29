# BG0849: A close dry run mints a different graduation change request id each time, so a retro cannot rule it before the close

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T08:37:44Z

## Summary

`sprint.py close --dry-run` reports the lesson-graduation change request it would file (LC-002 graduating -> CR01M3P4PW), and the next dry run names another id (CR01M3P45Z), and the real close a third (CR01M3P45S). A retro's `## Known issues carried` table cannot rule an id nobody can predict, so the new CR is always handed over UNRULED. Seen on the sdlc-studio.com web run RUN-01M3HRHY.

## Steps to Reproduce

In a run where a lesson class crosses its graduation threshold, run `sprint.py close --dry-run` twice and note the CR id each prints; run `sprint.py close`: a third id is filed, and the checklist reports it UNRULED.

## Proposed Fix

Derive the graduation CR's id deterministically for the run and class (or find the open CR for that class and reuse it), and let the dry run print the id the close will file; or rule a graduation CR by class rather than by id.

## Acceptance Criteria

- [ ] **AC1** Given a run whose close graduates a lesson class, when `sprint.py close --dry-run` runs twice and then `sprint.py close` runs, then all three name the same change request id.

## Impact

Every close that graduates a lesson hands over one known issue nobody could have ruled, which trains readers to ignore UNRULED.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
