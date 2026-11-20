# BG1669: reference-scripts-review.md does not describe persona_review.py owed

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-scripts-review.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T13:56:29Z

## Summary

Lane K's builder (RUN-01M7VNR0) added `persona_review.py` owed (US1057), which lists each card owed a review, but reference-scripts-review.md, the script catalogue page for the review scripts, does not describe the subcommand, so an agent looking for a tool before hand-rolling does not find it.

## Steps to Reproduce

grep -n owed .claude/skills/sdlc-studio/reference-scripts-review.md: no line describes `persona_review.py` owed.

## Proposed Fix

Add `persona_review.py` owed to reference-scripts-review.md's `persona_review.py` entry with its output and exit codes, then run docgen.py reading-guides.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Lane K's builder (RUN-01M7VNR0) added `persona_review.py` owed (US1057), which lists each card owed a review, but reference-scripts-review.md, the script...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep -n owed .claude/skills/sdlc-studio/reference-scripts-review.md: no line describes `persona_review.py` owed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add `persona_review.py` owed to reference-scripts-review.md's `persona_review.py` entry with its output and exit codes, then run docgen.py reading-guides.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
