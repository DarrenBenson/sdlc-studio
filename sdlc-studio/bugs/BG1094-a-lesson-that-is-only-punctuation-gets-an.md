# BG1094: A lesson that is only punctuation gets an empty heading title since BG1061

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_heading_empty.py, changelog.d/BG1094.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** BG1061 QA review, round 2 (APPROVE), qa-seat-BG1061-r1, 2026-10-19, at 20be66b1: [regression] item 2.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T19:54:10Z

## Summary

`lessons.heading_title` strips every trailing mark and drops the ellipsis when nothing is left, so a bare '- ?' or '- ...' bullet is extracted as '## L-0002:' with an empty title, which markdownlint refuses (MD026, MD009). Before BG1061 the same lesson was '## L-0002: ?'. Degenerate author-error input: the retro template's placeholder is filtered and no retro here has such a bullet.

## Steps to Reproduce

Extract a retro whose Lessons section holds a bullet '- ?' and read the log's heading.

## Proposed Fix

Fall back to the unstripped text when the strip leaves nothing.

## Acceptance Criteria

- [ ] **AC1** A punctuation-only lesson keeps a non-empty heading title
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_heading_empty.py::LessonsHeadingEmptyTests

## Impact

A punctuation-only lesson produces a heading the markdown lane refuses.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it needs a condition no real install meets. Degenerate author error: a lesson bullet that is only punctuation ('?' or '...'). No real lesson reads that way, and the retro template's placeholder is not affected. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
