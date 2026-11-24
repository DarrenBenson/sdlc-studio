# BG1458: escape.py to-class records a class with no files for a hand-edited bug with no Affects, collapses whitespace inside Affects paths, and the catalogue pages lag the new verb and flags

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_escape_class_edges.py, changelog.d/BG1458.md
> **Evidence:** Run thirteen (RUN-01M7EYR3) review of US1159, qa-seat-US1159-r1, verdict sdlc-studio/reviews/verdicts/US1159/337d1aaeeea2-f76babf3.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run thirteen orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T08:36:27Z

## Summary

Run thirteen's US1159 review (APPROVE, non-blocking): a bug hand-edited to carry no Affects still gets a failure class with an empty `files` list instead of a refusal; internal whitespace in an Affects path is collapsed when copied into `files`; and the detailed `### escape.py` section in reference-scripts-review.md and the class-add entries do not describe `to-class`, `--file` or `--evidence` yet.

## Steps to Reproduce

Remove a confirmed escaped bug's Affects line and run `escape.py to-class --bug BGxxxx`: a class with no files is written.

## Proposed Fix

Refuse a bug with no Affects, keep path whitespace as written, and document to-class and class-add's new flags on the catalogue pages.

## Acceptance Criteria

- [ ] **AC1** Given an escaped bug with no Affects, when to-class runs, then it refuses with the reason and writes nothing. Fails on: a class with empty files.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_class_edges.py::EscapeClassEdgeTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Escape.py edge cases on hand-edited bugs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run thirteen orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
