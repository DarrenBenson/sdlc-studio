# US0592: The goal seat review is enforced by sprint plan --write, so skipping it is refused where it can still be run

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, sdlc-studio/decisions.md
> **Epic:** EP0197
> **Depends on:** BG0516, BG0521, US0595
> **Points:** 5

## User Story

**As a** operator setting a sprint's direction
**I want** the goal seat review enforced at plan time
**So that** a seat can still refuse the goal while the batch can be re-cut

## Acceptance Criteria

### AC1: a plan with no Sprint Goal at all is refused, because omitting the goal is the free bypass

- **Given** `sprint plan --write` invoked with no `--sprint-goal`
- **When** the plan is written
- **Then** it is refused unless the recorded escape is taken, because the existing refusal is
  guarded on a goal being present: today a plan with no goal returns 0, opens the run, records
  `reviewed: False`, and the close then reports the item outstanding past its window - which is
  the flaw this story exists to end, surviving intact through its own fix
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_a_plan_with_no_sprint_goal_is_refused

### AC2: the recorded escape names its authoriser at the moment it is taken

- **Given** an operator who deliberately skips the seat review
- **When** the plan is written with the recorded opt-out
- **Then** the waiver is recorded then and there with its authoriser, so the decision is made when it can still be reconsidered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_the_escape_is_recorded_at_plan_time

### AC3: a reviewed goal plans without complaint

- **Given** a Sprint Goal carrying seat verdicts
- **When** the plan is written
- **Then** it succeeds silently - the control against a gate that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_a_reviewed_goal_plans_cleanly

## Test-plan notes

Written after a plan review rejected the first draft, which had found the story's headline
already shipped.

1. **The unreviewed-goal refusal already exists** in `cmd_plan` and is asserted verbatim by
   `GoalConsultTests::test_plan_refuses_a_sprint_goal_no_seat_has_reviewed`. A criterion re-
   asserting it would be green on HEAD before a line is written, and would open a second row
   answering a question an existing one already answers - the very flaw the parent CR is about.
   AC1 therefore moves to the part that does NOT exist: the refusal is guarded on a goal being
   present, so omitting `--sprint-goal` skips it for free.
2. **The escape is `--goal-review-waived <authoriser>`**, a new flag. `--skip-personas` is a
   general `store_true` used by roughly thirty call sites and carries no authoriser, so it
   cannot be the input. The waiver is recorded under the subject the close actually reads,
   `rule:sprint-checklist:goal-seat-reviewed`; AC2's test asserts it resolves through
   `decisions.waiver_for` against that item id, because a row written under a subject nothing
   reads is a defect this repo has already had twice.
3. **AC2 asserts the AUTHORISER's value**, not that a row exists. An implementation writing a
   constant or empty authoriser satisfies "a waiver was recorded" while failing the criterion,
   which is entirely about who authorised it. `record_waiver` already raises on an empty
   authoriser for this subject family, so the escape with no authoriser is refused; the test
   drives that too.
4. **AC3's mutant is the narrowest edit that breaks it.** Refusing the write path uncondit-
   ionally reddens 33 existing tests, so a new control test measures nothing; dropping the
   `not reviewed` term from the condition is the edit a careless implementer actually makes.
5. `Depends on` gains US0595, which changes the row `record_waiver` writes. Two units editing
   one row format in one sprint have to be ordered rather than hoped about.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | revert the goal-presence guard in sprint.py so the write path is reached with no goal recorded | a plan with no Sprint Goal at all is refused |
| AC2 | change sprint.py to pass a constant authoriser to the waiver rather than the one given on the command line | the recorded escape names its authoriser at the moment it is taken |
| AC3 | drop the `not reviewed` term from the refusal condition in sprint.py, so a reviewed goal is refused too | a reviewed goal plans without complaint |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
