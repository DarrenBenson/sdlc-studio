# US0860: a sprint goal is authored as numbered clauses each carrying a check, and `sprint plan --write` refuses a goal that carries none

> **Status:** Draft
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0258
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a sprint goal is authored as numbered clauses each carrying a check, and `sprint plan --write` refuses a goal that carries none
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: a goal is parsed into numbered clauses, each with its own check.**
  - **Given** a plan whose goal is two numbered lines, each carrying a `Check:` sub-field
  - **When** `sprint plan --write` runs
  - **Then** run state records two clauses, in order, each with its check text - the goal stops being one opaque string
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseAuthoringTests::test_a_numbered_goal_is_parsed_into_clauses_with_checks
- [ ] **AC2: a goal whose clauses carry no check is REFUSED at plan time.**
  - **Given** a plan whose goal is prose, exactly as every goal in this repository is written today
  - **When** `sprint plan --write` runs
  - **Then** it refuses, names the goal, and says a clause needs a check - the refusal is the whole mechanism, because a goal that can be written uncheckable will be
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseAuthoringTests::test_a_goal_with_no_checks_is_refused
- [ ] **AC3: the refusal names what is missing and suggests a check from the batch.**
  - **Given** the same prose goal, over a batch whose units carry `Verify:` selectors
  - **When** the refusal renders
  - **Then** it offers one of those selectors as a candidate check - a refusal whose cheap escape is a vaguer goal has made things worse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseAuthoringTests::test_the_refusal_suggests_a_check_from_the_batch
- [ ] **AC4: a well-formed goal still plans.**
  - **Given** a goal whose every clause carries a check
  - **When** `sprint plan --write` runs
  - **Then** it writes the plan - the discriminating half, because a gate that refused every goal would pass AC2 and deliver nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseAuthoringTests::test_a_well_formed_goal_plans
- [ ] **AC5: a clause survives a round trip through run state.**
  - **Given** a written plan with clauses
  - **When** run state is re-read by a later command
  - **Then** the clauses and their checks come back unchanged, including a check containing a pipe or a colon - the close reads these, and a clause mangled in storage fails silently at the far end
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalClauseAuthoringTests::test_a_clause_round_trips_through_run_state

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, store the goal as the single opaque string it is today, parsing no clause structure out of it | a goal is parsed into clauses |
| AC2 | in `sprint.py`, accept a goal whose clauses carry no check, warning instead of refusing | an uncheckable goal is refused |
| AC3 | in `sprint.py`, emit the refusal with no candidate drawn from the batch's `Verify:` lines | the refusal suggests a check |
| AC4 | in `sprint.py`, widen the refusal so it fires whenever a goal carries more than one clause | a well-formed goal still plans |
| AC5 | in `lib/run_state.py`, serialise a clause by joining its fields on a separator that its own check text may contain | a clause round trips |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
