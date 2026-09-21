# US0862: a persona-judged clause is refused at plan time unless it names what would falsify it, and its ruling is refused unless it records the alternative rejected

> **Status:** Draft
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0258
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a persona-judged clause is refused at plan time unless it names what would falsify it, and its ruling is refused unless it records the alternative rejected
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: a persona-judged clause names its falsifier at PLAN time or it is refused.**
  - **Given** a goal clause whose check is persona-judged and carries no `Falsifier:`
  - **When** `sprint plan --write` runs
  - **Then** it refuses and names the clause - at plan time, because the point of a falsifier is that it is fixed before the work makes it inconvenient
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PersonaClauseGuardTests::test_a_persona_clause_without_a_falsifier_is_refused_at_plan_time
- [ ] **AC2: a persona ruling is refused unless it records the alternative it rejected.**
  - **Given** a seat ruling on such a clause with a verdict and a rationale but no rejected alternative
  - **When** the ruling is recorded
  - **Then** it is refused - a ruling with nothing rejected is assent, and assent dressed as governance is worse than an escalation
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PersonaClauseGuardTests::test_a_ruling_with_no_rejected_alternative_is_refused
- [ ] **AC3: a complete ruling records its seat, rationale and rejected alternative.**
  - **Given** a ruling carrying all three
  - **When** it is recorded
  - **Then** all three survive into run state and are readable by the report - the discriminating half
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PersonaClauseGuardTests::test_a_complete_ruling_is_recorded_with_all_three_fields
- [ ] **AC4: a selector-shaped clause is NOT asked for a falsifier.**
  - **Given** a clause whose check is an ordinary selector
  - **When** the plan is written
  - **Then** it is accepted without one - the obligation attaches to the judged shape alone, and applying it to every clause would make the cheap path the vague one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PersonaClauseGuardTests::test_a_selector_clause_needs_no_falsifier

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, defer the falsifier check from plan time to close time, so the clause is authored first and constrained later | a falsifier is demanded at plan time |
| AC2 | in `critic.py`, accept a persona ruling that records no rejected alternative | a ruling names what it rejected |
| AC3 | in `critic.py`, drop the rejected alternative when persisting a ruling, keeping only seat and rationale | a complete ruling keeps all three |
| AC4 | in `sprint.py`, demand a falsifier from every clause rather than only the persona-judged ones | a selector clause needs none |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
