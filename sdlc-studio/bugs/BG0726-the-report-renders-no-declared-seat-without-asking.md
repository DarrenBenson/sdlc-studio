# BG0726: the report renders NO DECLARED SEAT without asking whether the project declares any personas at all

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 18, still true. `critic.py`'s own docstring requires callers to distinguish a project with NO PERSONAS from a reviewer with no seat, and `critic._seat_drift_warning` does exactly that - it is the one compliant caller. `sprint_report.py:1941` renders `seat or 'NO DECLARED SEAT'` and asks nothing, so on a project that has declared no personas every reviewer is labelled as having failed to declare a seat. The label accuses the reviewer of an omission that belongs to the project's configuration.

## Steps to Reproduce

1. Build a report on a workspace with no persona cards. 2. Every reviewer row reads NO DECLARED SEAT. 3. Compare with `critic._seat_drift_warning`, which asks first and says something different.

## Proposed Fix

Have the renderer ask `critic._declared_reviewers` (or the same predicate `_seat_drift_warning` uses) before labelling, and render a distinct phrase - `no seats declared on this project` - when the project declares none. Pin both branches.

## Acceptance Criteria

### AC1: a project that declares no personas is labelled differently from a reviewer with no seat

- **Given** two workspaces - one declaring persona cards where a reviewer records no seat, and one declaring no personas at all
- **When** the report renders its reviewer rows
- **Then** the first reads NO DECLARED SEAT and the second reads a distinct phrase naming the project's configuration, so the label never accuses a reviewer of an omission that is not theirs
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/sprint_report.py`, render `seat or 'NO DECLARED SEAT'` without asking whether any persona is declared - every reviewer on a persona-less project is then reported as having failed to declare a seat
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SeatLabelTests::test_a_persona_less_project_is_not_reported_as_a_reviewer_omission

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
