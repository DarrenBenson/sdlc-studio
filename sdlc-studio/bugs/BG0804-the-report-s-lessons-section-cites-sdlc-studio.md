# BG0804: The report's Lessons section cites sdlc-studio/lessons.jsonl on a project that has none, when the bundled seed was read

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG0804.md
> **Severity:** Low
> **Points:** 1

## Summary

CR0592 bullet (file line 31) re-measured at f76b70cc: on a fresh project the Lessons section sources all 8 rows to `sdlc-studio/lessons.jsonl`, a file that does not exist; `lessons.store_source()` already returns the right label and `_lessons_section` uses `lessons.STORE_FILE` instead.

## Steps to Reproduce

`sprint_report._lessons_section` on a fresh init project with no lessons.jsonl.

## Proposed Fix

Read the source label from `lessons.store_source().`

## Acceptance Criteria

- [ ] **AC1** Given a project with no `sdlc-studio/lessons.jsonl`, when the report's Lessons section is built, then every figure's source is the bundled seed's label, and with a store present it is `sdlc-studio/lessons.jsonl`. Fails on: citing `lessons.STORE_FILE` unconditionally (HEAD)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::LessonsSourceTests::test_the_lessons_section_cites_the_store_it_read

## Notes

First-week: every fresh project's first report cites a missing file, on the page whose claim is that every figure names its source. Mint from CR0592 and remove the bullet.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0804) |
