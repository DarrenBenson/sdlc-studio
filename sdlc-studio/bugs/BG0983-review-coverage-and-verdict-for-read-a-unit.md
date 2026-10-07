# BG0983: `review_coverage` and `verdict_for` read a unit's whole per-unit ledger, so an APPROVE from an earlier delivery covers a re-delivered unit that nobody reviewed in this run

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_coverage_scoped_to_the_run.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0983.md
> **Evidence:** BG0962 round-1 QA review, 2026-10-07 (probe P26); reproduced by the author the same day.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T13:28:22Z

## Summary

The run fixes each unit's `REVIEW_BASE` (its verdict-row count before its first review in the run), and `critic.delivery_rounds` and `cited_lessons` read only the rows past it. `sprint.review_coverage` (sprint.py:5225) and `critic.verdict_for` (critic.py:700) do not: they read every row the unit has ever had. So a unit re-delivered in a later run, a reopened bug or a story moved back, carries its earlier delivery's APPROVE into the new run, and the close counts it covered with no review of the new change. Reproduced on 2026-10-07: a per-unit APPROVE dated 2026-08-01, a run opened 2026-10-01, no review in the run -> `review_coverage` {covered: True, by: per-unit verdict} and closing-review `ran`. Found by BG0962's round-1 QA reviewer (probe P26 at 8b844a80); BG0962's fold inherits it.

## Steps to Reproduce

Record a per-unit APPROVE for a unit; open a later run whose batch holds the unit; record no review in it; `sprint.py close --dry-run` -> review-coverage and closing-review both pass.

## Proposed Fix

Read coverage and the per-unit verdict from the unit's rows past the run's `REVIEW_BASE`, as `delivery_rounds` does, falling back to the whole ledger only for a unit the run never based (outside a run).

## Acceptance Criteria

- [ ] **AC1** A unit whose only APPROVE predates the open run's `REVIEW_BASE` for it is not covered, and closing-review holds it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_coverage_scoped_to_the_run.py -k an_earlier_delivery_approve_does_not_cover
- [ ] **AC2** An APPROVE recorded in the open run still covers the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_coverage_scoped_to_the_run.py -k an_approve_in_the_run_covers
- [ ] **AC3** Outside a run, coverage still reads the whole ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_coverage_scoped_to_the_run.py -k outside_a_run_the_whole_ledger_counts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
