# BG1146: lessons.py revalidate --close appends its Status bullet straight after a paragraph, so the lessons log fails markdownlint MD032

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py, changelog.d/BG1146.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** 2026-11-01: `node_modules/.bin/markdownlint sdlc-studio/retros/LESSONS.md` after US1105 reported MD032 at the Status lines of L-0040 and L-0021. The log before US1105 (43626a1c) had no errors.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T02:09:00Z

## Summary

`close_entry` (lessons.py) writes `entry['body'].rstrip() + '\n' + '- **Status:** Closed - <reason>'`. A lesson whose body ends in a paragraph line (here 'Recorded from retro RETROnnnn.') then gets a list item with no blank line before it, which markdownlint refuses as MD032 blanks-around-lists. US1105's two closes, L-0040 and L-0021, put two such errors in sdlc-studio/retros/LESSONS.md on 2026-11-01. The orchestrator fixed them by hand.

## Steps to Reproduce

1. In a throwaway project, write a lesson whose body ends in a paragraph line.
2. `lessons.py revalidate --close L-0001 --reason x`.
3. Run markdownlint on the log: MD032 at the Status line.

## Proposed Fix

Separate the appended bullet from a preceding non-list line with one blank line, and check the same for the Revalidated bullet BG1139 writes.

## Acceptance Criteria

- [ ] **AC1** A close of a lesson whose body ends in a paragraph line leaves the log clean under the repository's markdownlint config.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py
- [ ] **AC2** A close of a lesson whose body already ends in a list item adds no stray blank line (the positive control).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lesson_lifecycle.py

## Impact

Every close made in a re-validation pass breaks the markdown lane for the next commit made in the main tree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
