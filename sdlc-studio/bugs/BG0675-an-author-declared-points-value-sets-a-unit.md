# BG0675: an author-declared Points value sets a unit's review tier: route.estimate's spec subscore reads Points, which D0150 rules out of review depth

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

route.estimate weights `spec` at 0.25 (route.py:54) and derives it from the unit's `Points` (route.py:103-147). The band feeds `critic.tier_for` via `plan_review._difficulty_band`, which sets the review depth a brief asks for, and `plan_review`'s difficulty trigger. D0150: 'No author-declared field may gate review depth ... Points, Severity, Size, or any field like them'. Measured on one throwaway unit (two Affects files, one AC), changing ONLY Points from 1 to 8 moves the score 30 -> 43, the band low -> medium and `critic.tier_for` light -> full. CR0549, which diagnosed the estimator, is Superseded; the Blocked US0677/US0678/US0684 carry diff-basis residue but none removes Points from the band in force. Found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. In a throwaway workspace, one story with Affects of two files and one AC, Points 1: `route.estimate` gives 30/low and `critic.tier_for` gives light.
2. Change only the Points field to 8: 43/medium and full.

## Proposed Fix

Remove the author-declared input from the subscore wherever the band decides review depth, deriving `spec` from a signal the author does not declare (or from the diff once a diff basis exists). If D0150 was meant more narrowly than this, record that as a decision instead and close this as ruled.

## Acceptance Criteria

- [ ] **AC1** A unit's review tier from `critic.tier_for` does not change when only its Points field changes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::TierIgnoresDeclaredFieldsTests::test_points_alone_does_not_move_the_tier
- [ ] **AC2** route.estimate's difficulty score does not change when only a unit's Points field changes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DeclaredFieldsDoNotScoreTests::test_points_alone_does_not_move_the_score
- [ ] **AC3** A change to a non-declared signal (the unit's Affects breadth) still moves the score - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DeclaredFieldsDoNotScoreTests::test_affects_breadth_still_moves_the_score

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
