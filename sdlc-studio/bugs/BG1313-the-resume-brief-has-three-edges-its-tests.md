# BG1313: The resume brief has three edges its tests do not pin: a batch listed out of plan order, a `-qa.none` landing marker read as in flight, and a Sprint Goal holding a newline that breaks `parse`

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py, changelog.d/BG1313.md
> **Evidence:** US1140-verdict-r1 findings 3-5 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:59:41Z

## Summary

From US1140's QA review (qa-seat-US1140-r1, non-blocking findings 3-5, 2026-11-09). (3) Five code mutants survive `test_resume_brief.py`; the main gap is that no fixture lists its batch in a different order from its plan, so an ordering mutant goes unseen. (4) A landing that wrote a `<unit>-qa.none` marker (no brief written) still reads as in flight rather than as landed with no brief. (5) A Sprint Goal containing a newline breaks the brief's round trip through `resume_brief.parse`. BG1312's review (qa-seat-BG1312-r1, findings 1-2) adds two: no test checks the 'run's findings cannot be placed' note is absent when the run has a start time, and no test pins the word boundary on the run-id stamp match.

## Steps to Reproduce

1. Run the reviewer's surviving mutants against `test_resume_brief.py` (US1140-verdict-r1, finding 3).
2. Build a brief for a run where a unit's landing left `.local/briefs/<unit>-qa.none`: it shows the unit in flight.
3. Build and parse a brief for a run whose Sprint Goal holds a newline: the parse does not return the goal.

## Proposed Fix

Add a fixture whose batch order differs from its plan, read a `-qa.none` marker as landed with no brief, and fold or refuse a newline in the goal before rendering; pin each with a test that fails under its mutant.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose batch lists its units in a different order from its plan's waves, when the resume brief is built, then its unit rows and its next action follow the plan's wave order. Fails on: rows in batch order, the ordering mutant US1140's review found alive.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_a_batch_listed_out_of_plan_order_is_briefed_in_plan_order
- [ ] **AC2** Given a unit marked in flight whose landing left `<unit>-qa.none` and no QA brief, when the brief is built, then the unit reads as landed with no brief, and the next action does not await its lane. Fails on: rung 1 awaiting a lane that has already landed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_a_landing_that_left_a_qa_none_marker_is_not_in_flight
- [ ] **AC3** Given a run whose Sprint Goal holds a newline, when `sprint.py handoff` builds the brief and `resume_brief.parse` reads it back, then the goal is returned whole with the newline folded to a space. Fails on: the parse returning only the goal's first line, or none.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_a_goal_holding_a_newline_survives_the_round_trip
- [ ] **AC4** Given a run with a recorded start, and an open finding stamped with a run id that only begins with the open run's id, when the brief is built, then that finding is left out and no 'cannot be placed' note is printed. Fails on: a prefix match listing another run's finding, or the note shown for a run that has a start.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::KnownIssuesTests::test_a_longer_run_id_is_not_matched_and_a_started_run_prints_no_placement_note

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Three untested resume-brief edges.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
