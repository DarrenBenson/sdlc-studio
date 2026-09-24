# BG0729: the batch-level reviewer contribution to the lens count is asserted by no test

> **Status:** Won't Fix
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 21, still true. `sprint_report.py:1946-1947` unions reviewers from `sprint_reviews` and `review_rounds` into the lens count. A scripted scan of `test_sprint_report.py` finds zero occurrences of `reviewer` within 400 characters of any assignment to either key, so deleting the union changes no asserted figure. The lens count is a confidence figure on the report of record, and half of its input is unpinned.

## Steps to Reproduce

1. Delete the `sprint_reviews`/`review_rounds` reviewer union from the lens count. 2. Run the whole of `test_sprint_report.py.` 3. Green.

## Proposed Fix

Add a fixture placing a reviewer ONLY in `review_rounds` and another only in `sprint_reviews`, and assert the lens count rises for each - so gutting the union reddens. This is the mutant the criterion should have named when the union was written.

## Acceptance Criteria

### AC1: the batch-level reviewer contribution to the lens count is pinned

- **Given** a report fixture placing a reviewer ONLY in `review_rounds`, and a second placing one only in `sprint_reviews`
- **When** the lens count is derived
- **Then** it rises for each, so removing either union reddens a test
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, delete the `sprint_reviews`/`review_rounds` reviewer union from the lens count - the figure then drops on every run with a batch-level review and no test says so
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::LensCountTests::test_a_batch_level_reviewer_raises_the_lens_count

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - unasserted lens-count input: test gap in a figure the one-page report dropped |
