# US0596: Coverage is computed once, and two rows disagreeing about it is itself an outstanding item

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0197
> **Points:** 3

## User Story

**As a** operator reading one report
**I want** coverage computed once
**So that** a close cannot report three different answers to one question

## Acceptance Criteria

### AC1: coverage has one computation

- **Given** the close chain, the checklist coverage row and the review row
- **When** a close composes its report
- **Then** all three read one computed value, so a run cannot report `9/9 covered`, `0 covered, 37 uncovered` and `71 recorded passes` about the same question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CoverageConsistencyTests::test_coverage_has_one_source

### AC2: a disagreement is itself outstanding

- **Given** a report in which two coverage readings differ
- **When** the checklist resolves
- **Then** the disagreement is an OUTSTANDING item naming both readings, because a report contradicting itself is a fact about the report that nothing currently notices
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CoverageConsistencyTests::test_a_disagreement_is_outstanding

### AC3: two agreeing readings resolve answered

- **Given** a report whose readings agree
- **When** the checklist resolves
- **Then** the row is ANSWERED - the control, because `_resolve_item` turns any resolver
  exception into the same UNANSWERED that holds the close, so a row that crashes on every
  input satisfies AC2 without computing anything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CoverageConsistencyTests::test_two_agreeing_readings_are_answered

## Test-plan notes

Written after a plan review rejected the first draft.

1. **The criterion names THREE readers and all three must read the one value.** They are
   `sprint._close_review_coverage` (via `sprint.review_coverage`), `_ck_closing_review`, and
   `_ck_review_attribution`. `Affects` now carries `sprint.py` because one of them lives there;
   rewiring only the row this story mentions and leaving the other two computing independently
   is the careless implementation, and it must not survive.
2. **The fixture has to make them DISAGREE.** On two units with one clean APPROVE each, every
   independent recompute agrees and "recompute its own figure" changes no output - the test then
   measures nothing. The fixture carries a repaired REJECT and a batch-level review naming a
   unit, over a batch that is a strict subset of the report's units: the three lane rules that
   produced `9/9`, `0 covered, 37 uncovered` and `71 recorded passes` about one question. The
   assertions are on the NUMBER, not on two calls being equal.
3. **AC2 asserts both readings appear in the row**, not only that the row is outstanding.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | revert `_ck_closing_review` in sprint_report.py to counting `ctx['sprint_reviews']` itself instead of reading the shared figure | coverage has one computation |
| AC2 | drop one of the two readings from the row's value in sprint_report.py | a disagreement is itself outstanding |
| AC3 | change sprint_report.py to return the disagreement state whatever the two readings are | two agreeing readings resolve answered |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
