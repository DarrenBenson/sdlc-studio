# US1038: The QA seat's goal-review brief lists the batch criteria no executable check covers

> **Status:** Draft
> **Delivers:** CR0627
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_qa_manual_criteria.py, changelog.d/US1038.md
> **Epic:** EP0284
> **Points:** 2
> **Depends on:** US1037
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose last run left walk-tests owed by the operator
**I want** the QA seat's goal-review brief to list each batch criterion whose Verify line is manual or missing
**So that** QA can ask for an executable check at plan time, before a manual check is left owed at the close

## Acceptance Criteria

- **AC1:** Given a batch unit with one `Verify: manual` criterion and one with no Verify line, when `goal-review brief --seat qa` runs, then it names both criteria by unit and id as manual and unspecified, and the engineering seat's brief does not carry the list
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_qa_manual_criteria.py::QaManualCriteriaTests::test_the_qa_brief_names_each_unexecutable_criterion
- **AC2:** Given a batch whose every criterion has an executable Verify line, when the QA brief runs, then it says every criterion in the batch is executable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_qa_manual_criteria.py::QaManualCriteriaTests::test_a_fully_executable_batch_says_so

## Notes

- Release: 6.2 (D0355 breakdown G10, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the list is built from the plan's ungroomed field, which names placeholder criteria only, or is given to every seat
- AC2 must fail on: an empty list prints nothing, so a seat cannot tell none from not checked
- Classified by verify_ac.parse_story and a public alias of verify_ac._is_manual, the runner's own reading, so the brief and `verify_ac run` cannot disagree on what manual means (LL0016).
- The units are the brief's batch, which is BG1002's live batch.
- Last in the goal-review cluster, after the seat questions story: all of them change the same two brief functions, so they are built in sequence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G10 after the refine panel's review |
