# BG1180: The PRD's section 8 says git fetch origin serves remote-aware id allocation, which section 5 and next_id.py contradict: id allocation never fetches

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1180.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:06:39Z

## Summary

Found by the release triage and BG1176's review (2026-11-02). prd.md:588-589 says `git fetch origin` serves 'remote-aware id allocation'. prd.md:500 says id allocation reads `origin/main` with `git ls-tree` and never fetches, and `next_id.py`:7 agrees. US1104 (8f380767) corrected one of the two places.

## Steps to Reproduce

1. `grep -n 'remote-aware id allocation' sdlc-studio/prd.md`.
2. `sed -n 1,12p .claude/skills/sdlc-studio/scripts/next_id.py`.

## Proposed Fix

Reword section 8 to name what does fetch (`sprint.origin_drift`) and say id allocation reads origin/main without fetching.

## Acceptance Criteria

- [ ] **AC1** No PRD sentence says id allocation fetches, and the PRD refresh test fails if one does.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py

## Impact

The PRD states a network behaviour the code does not have.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
