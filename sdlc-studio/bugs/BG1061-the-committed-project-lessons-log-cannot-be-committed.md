# BG1061: The committed project lessons log cannot be committed where markdownlint's defaults apply: every lesson heading ends in its sentence's punctuation, which MD026 refuses

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_lints.py, changelog.d/BG1061.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** RUN-01M4R168 close commit, 2026-10-16: the pre-commit `markdown` lane refused sdlc-studio/retros/LESSONS.md with MD026 at 7:138, 14:149 and 23:126, the three headings RETRO0134's extract wrote; the log was left uncommitted in the closing clone. lessons.py:153 `## {id}: {title}`; retro.py:492 `lesson_title`; .markdownlint.json `"default": true` with MD026 not disabled.
> **Created:** 2026-10-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-16T10:03:13Z

## Summary

BG0989 moved the project lessons log from the gitignored `.local/lessons.md` to the committed `sdlc-studio/retros/LESSONS.md`, so it is now linted like any tracked markdown. Each entry is written as `## L-NNNN: <title>` (lessons.py:153), and the title is the lesson's first complete sentence, full stop included, or an elision ending in `...` (`lesson_title`, retro.py:492). markdownlint's MD026 (no trailing punctuation in a heading) is on by default and on in this repo's `.markdownlint.json`, so every heading fails it, and the pre-commit `markdown` lane refuses the commit that adds the log. While the log lived in `.local/` it was never linted, which is how the shape survived; the digest `LESSONS-SUMMARY.md` renders lessons as bullets and is unaffected.

## Steps to Reproduce

1. On a clone with no project lessons log, run `retro.py extract --id RETROxxxx` on a retro whose Try items are sentences. 2. `git add sdlc-studio/retros/LESSONS.md && git commit` -> `FAIL markdown`: `sdlc-studio/retros/LESSONS.md:7:138 error MD026/no-trailing-punctuation Trailing punctuation in heading [Punctuation: '.']`, one per entry.

## Proposed Fix

Write the heading without its trailing sentence punctuation (strip it in the heading render, keeping the full sentence in the body), reading the existing log's headings the same way so they do not churn; or render each entry's title as bold text rather than a heading.

## Acceptance Criteria

- [ ] **AC1** A project lessons log written by `retro.py extract` has no heading with trailing punctuation (markdownlint MD026, on by default), so the commit that adds it passes the repository's markdown lane
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_lints.py -k extracted_log_has_no_trailing_heading_punctuation
- [ ] **AC2** Given an existing log whose headings end in their sentence's punctuation (the shape every log written before this fix has), when it is read and a further retro is extracted into it, then every existing lesson keeps its id and title, nothing is added twice, and the lessons the summary lists are still found
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_log_lints.py -k an_existing_punctuated_log_reads_without_churn

## Impact

The log BG0989 made committed cannot be committed in this repository, or in any consuming project running markdownlint's defaults, without a hook bypass or a lint exemption.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-16 | Claude Opus 5.5 | Filed |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: AC1 names MD026, AC2 pins the no-churn read of an existing log |
