# US1082: The PRD's outcome citations name End goals that say them, and Jonah's upgrade goal has an outcome

> **Status:** Ready
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/US1082.md
> **Epic:** EP0289
> **Points:** 1
> **Depends on:** US1081
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading the PRD's outcomes to judge whether a run served a persona
**I want** each outcome to cite an End goal that says it, and every End goal of the personas the PRD serves to have an outcome
**So that** a goal trace through the PRD means what it claims

## Acceptance Criteria

- **AC1:** Given the PRD's outcome citations and the cards they cite, when each persona the outcomes cite is read, then every one of its End goals is cited by at least one outcome, and no persona and End goal pair is cited by two outcomes
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_every_end_goal_is_cited_once
- **AC2:** Given outcome O5, when its citation is read, then it cites Maya Okafor's End goal 5, and an outcome cites Jonah Reyes's End goal 4
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_o5_and_jonahs_upgrade_goal_are_cited
- **AC3:** Given Jonah Reyes's card, when its End goals are read, then End goals 1 to 4 are word for word what they are at the run's base ref
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_jonahs_end_goals_are_unchanged

## Notes

- Serves: Maya Okafor, End goal 4.
- Delivers CR0648:27 (EP0289:30): no maintainer outcome (D0380). Today O5 (prd.md:103, 'the process stays small enough to serve the work') cites Maya End goal 3, which does not say it, and Jonah End goal 4 ('Upgrade safely as the skill evolves') is cited by no outcome. `outcome_problems` checks only that a cited card and number exist, so both pass today.
- Whether a goal says an outcome is a judgement; AC2 pins the two citations the consult ruled, and the reviewer judges the wording.
- AC1 must fail on: O5 still citing Maya End goal 3 (a pair cited twice); Jonah End goal 4 uncited.
- AC2 must fail on: O5 re-pointed to any other goal.
- AC3 must fail on: Jonah's End goal 4 reworded to fit an outcome (a goal change under D0374).
- Depends on US1081, which appends Maya End goal 5 if the operator approves it. Without it, O5 needs another citation and AC2 changes with that ruling.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | sdlc-studio | Retitled: was "The PRD's outcomes cite End goals the cards state, and Jonah's upgrade goal has an outcome" |
