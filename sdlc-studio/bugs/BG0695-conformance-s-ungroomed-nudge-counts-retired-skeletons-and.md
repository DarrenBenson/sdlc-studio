# BG0695: conformance's ungroomed nudge counts retired skeletons and tells the user to groom Superseded and Won't Implement stories before planning them to Done

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_ungroomed_count.py, changelog.d/BG0695.md
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

- [ ] **AC1** Given a fixture holding one Superseded and one Won't Implement story, each still carrying the refine ungroomed-AC placeholder, and one Draft story carrying it, when `conformance.py check` runs, then the summary counts 1 ungroomed story and the groom nudge names 1. Fails on: HEAD, which counts all three (this repository at 013a46d0 is told to groom 124 stories, about 110 of them retired by the D0265 sweep)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_ungroomed_count.py::UngroomedCountTests::test_retired_stories_are_not_counted_ungroomed
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a fixture whose only placeholder stories are Superseded or Won't Implement, then no groom nudge line is printed. Fails on: a fix that subtracts retired stories from the count but still prints the nudge at zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_ungroomed_count.py::UngroomedCountTests::test_no_nudge_when_only_retired_stories_carry_the_placeholder
  - **Verified:** yes (2026-09-25)

## Notes

- The Summary's second half (the live retired-story test deciding whether to run by checking for the US0719, US0797 and US0798 files instead of `workspace.in_dev_repo()`) is test hygiene; fold it in only if the same test file is touched, otherwise it rides with CR0592's remainder.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-25 | sdlc-studio v6 planning | QA seat: generic AC1 replaced with falsifiable criteria for Sprint 5 (reproduced at 013a46d0: 124 counted) |
