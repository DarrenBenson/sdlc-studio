# BG1740: reference-review.md lists the optional claim surfaces without the declared pages

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md
> **Evidence:** run twenty-five, BG1591 qa review rounds one and two
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson (qa); persona; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T13:36:01Z

## Summary

reference-review.md:476 says docstrings, comments, Resolutions and CHANGELOG are optional claim surfaces, but since BG1591 the author self-check also inventories and rules each declared page (read from `claim_surfaces`). An author following the page leaves page claims unruled.

## Steps to Reproduce

1. Read reference-review.md's AUTHOR SELF-CHECK paragraph. 2. Compare with `critic.py brief` step 1 for a unit declaring a page.

## Proposed Fix

Name the declared pages among the optional surfaces in that sentence.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reference-review.md:476 says docstrings, comments, Resolutions and CHANGELOG are optional claim surfaces, but since BG1591 the author self-check also...
- [ ] **AC2** The proposed fix lands, pinned by a test: Name the declared pages among the optional surfaces in that sentence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | Sam Eriksson (qa) | Filed |
