# BG1093: BG1061's heading checks read a heading's trailing space as its last character, so a mark left behind a space passes

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_lints.py, changelog.d/BG1093.md
> **Evidence:** BG1061 QA review, round 2 (APPROVE), qa-seat-BG1061-r1, 2026-10-19, at 20be66b1: [new] item 1.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T19:53:57Z

## Summary

`test_lessons_log_lints.py` reads head[-1] and newest[-1], the heading line's last character. MD026 trims trailing whitespace before it looks, so a `heading_title` that strips the marks but not the space writes a heading ending in ': ' that markdownlint refuses (MD026, plus MD009) while all three tests pass. The final markdownlint run misses it because the next add re-renders that heading. The AC1 docstring and the EDGES comment name this mutant as killed.

## Steps to Reproduce

Mutate `lessons.heading_title` to strip the ASCII marks but not a trailing space, then run `test_lessons_log_lints.py`: green.

## Proposed Fix

Check head.rstrip()[-1] and newest.rstrip()[-1], and refuse trailing whitespace on a heading.

## Acceptance Criteria

- [ ] **AC1** A `heading_title` that leaves a trailing space after stripping turns the lessons log tests red
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_heading_space.py::LessonsHeadingSpaceTests

## Impact

A regression in the heading strip can pass the suite.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
