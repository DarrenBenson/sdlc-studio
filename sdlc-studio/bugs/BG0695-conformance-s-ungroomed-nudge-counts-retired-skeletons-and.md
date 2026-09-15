# BG0695: conformance's ungroomed nudge counts retired skeletons and tells the user to groom Superseded and Won't Implement stories before planning them to Done

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0669-delivery-qa.txt (qa seat); verdicts/BG0669-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. Queued in findings/todo.txt as FILE AT CLOSE. The vocabulary over-claim the same verdicts raised is already corrected in conformance.py and changelog.d/BG0669.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The ungroomed count and its nudge (conformance.py:777, 802 and 980 at review) count every story still carrying the refine placeholder, retired ones included, and print 'groom them (author real ACs and a Verify line) before planning to Done' for a Superseded or Won't Implement story, which the same lane now exempts from the specified and verifiable stages. 3f73ab64 prints the same; unfiled until now. Separately, the live half of the retired-story test decides whether it runs by checking for the US0719, US0797 and US0798 files (`test_conformance.py`:1950-1952) instead of the shared tests/workspace.py `in_dev_repo()`, so a project with a project-local install whose ids reach US0798 would run the live half against its own decision log and fail.

## Steps to Reproduce

In a fixture, write a story at Superseded whose Acceptance Criteria are the refine ungroomed marker, then run python3 .claude/skills/sdlc-studio/scripts/conformance.py check - the summary counts it as ungroomed and tells the user to groom it before planning to Done.

## Proposed Fix

Leave `retired_story_statuses()` out of the ungroomed count and the nudge; gate the live half on `in_dev_repo().`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The ungroomed count and its nudge (conformance.py:777, 802 and 980 at review) count every story still carrying the refine placeholder, retired ones included...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fixture, write a story at Superseded whose Acceptance Criteria are the refine ungroomed marker, then run python3...
- [ ] **AC3** The proposed fix lands, pinned by a test: Leave `retired_story_statuses()` out of the ungroomed count and the nudge; gate the live half on `in_dev_repo().`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
