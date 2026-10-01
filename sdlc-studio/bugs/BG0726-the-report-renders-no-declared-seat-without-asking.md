# BG0726: the report renders NO DECLARED SEAT without asking whether the project declares any personas at all

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_seat_label.py, changelog.d/BG0726.md
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: a fixture with no persona cards and one APPROVE by 'Priya Raman' renders `US0001 by Priya Raman (NO DECLARED SEAT)` in the review-attribution row; `init` writes no seat cards, so every fresh v6 project reads this.

BG0463 claim 18, still true. `critic.py`'s own docstring requires callers to distinguish a project with NO PERSONAS from a reviewer with no seat, and `critic._seat_drift_warning` does exactly that - it is the one compliant caller. `sprint_report.py:1941` renders `seat or 'NO DECLARED SEAT'` and asks nothing, so on a project that has declared no personas every reviewer is labelled as having failed to declare a seat. The label accuses the reviewer of an omission that belongs to the project's configuration.

## Steps to Reproduce

1. Build a report on a workspace with no persona cards. 2. Every reviewer row reads NO DECLARED SEAT. 3. Compare with `critic._seat_drift_warning`, which asks first and says something different.

## Proposed Fix

Remove the false label rather than add a phrase: render the seat parenthetical only when `critic._declared_reviewers` returns any seat (the predicate `_seat_drift_warning` already asks). On a project that declares none, the row reads `US0001 by Priya Raman`. Nothing new is reported.

## Acceptance Criteria

- [ ] **AC1** Given a fixture with no persona cards and one APPROVE by `Priya Raman`, when `sprint_report.py --root <fixture> checklist --id RETRO9100 --format json` renders the `review-attribution` row, then the row names `US0001 by Priya Raman` and does not contain `NO DECLARED SEAT`; with a `personas/seats/qa.md` card declaring another person, a reviewer matching no seat still reads `NO DECLARED SEAT`. Fails on: HEAD renders `(NO DECLARED SEAT)` on the persona-less fixture
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seat_label.py::SeatLabelTests::test_a_persona_less_project_is_not_reported_as_a_reviewer_omission

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD; fix re-scoped to dropping the false label (no new phrase); Points 2 to 1; Affects gains the lean test and changelog fragment |
