# CR-0657: Lesson Revalidated reasons cite file:line evidence that drifts as code lands; check and re-anchor it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Enhancement
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, .claude/skills/sdlc-studio/help/lessons.md, sdlc-studio/retros/LESSONS.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Date:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T04:07:59Z

## Summary

CR0655's re-validation pass (US1105-US1109) records each judgement as a Revalidated reason citing file:line evidence. Line numbers drift whenever code above them changes: when BG1109 added 16 lines to critic.py, 32 of US1108's citations went 16 lines short (qa-seat-US1108-r1, 2026-11-01). The critic.py citations in US1105-US1107, approved before BG1109 landed, are now 16 short as well. Nothing checks that a cited line still holds what the reason says, so the log's evidence silently decays between passes.

## Impact

The next re-validation pass, and any reader in between, meets citations that point at the wrong lines, and a reviewer re-running them wastes a round, as US1108's did.

## Acceptance Criteria

- [ ] `lessons.py revalidate --check-citations` reports every Revalidated reason whose `path:line` citation points past the file's end, or whose named symbol is no longer within a few lines of the cited line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] The re-validation guidance asks a reason to name the symbol beside each line, and the critic.py citations in L-0001 to L-0270 are re-anchored to the current tree.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Raised |
