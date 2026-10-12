# US1072: The close records each traced persona's served-goal outcome in its memory, with its run

> **Status:** Draft
> **Delivers:** CR0634
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_served_goal.py, changelog.d/US1072.md
> **Epic:** EP0287
> **Points:** 3
> **Depends on:** US1058, US1060, US1069
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose Sprint Goals name the persona they serve
**I want** the close to record, in each traced persona's memory, the Sprint Goal's verdict for that run with each traced End goal's result and its plan baseline
**So that** a user persona accumulates evidence, run by run, of whether the work served it

## Acceptance Criteria

- **AC1:** Given a run whose Sprint Goal names Maya Okafor, judged partial, with End goal 4 red at the close, when `sprint.py close` runs, then Maya's memory gains one entry with State observed naming the run, the goal, the verdict and End goal 4's result, and a second close of the same run refreshes that entry rather than adding one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_served_goal.py::ServedGoalOutcomeTests::test_the_close_records_a_traced_personas_goal_outcome_once
- **AC2:** Given the same run, when it closes, then Jonah Reyes, whom the goal does not trace to, and Trevor Hale, a Negative persona named through `--serves`, gain nothing, and a run with no goal verdict records nothing and says so in the close output.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_served_goal.py::ServedGoalOutcomeTests::test_only_designed_for_traced_personas_with_a_verdict_are_recorded

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: an entry per close attempt, or the outcome recorded without its run or its End goal results
- AC2 must fail on: every persona card written to, a Negative persona recorded as served, or a missing verdict recorded as an outcome
- Serves: Maya Okafor #4.
- Checked at HEAD: the goal verdict is kept on the run state (`sprint_goal_verdict`, sprint.py:5848) and `goal_trace` (:10000) names the personas a goal traces to, but nothing records the outcome against the persona.
- Carries the End goal results the CR0629 close story records, and the plan baseline when the baseline story recorded one ('turned green this run' is the strongest usage evidence).
- Written by the `persona-memory` close stage; observed entries are evidence, not learnings, and are never live (D5 injects approved learnings).
- Panel cut order: shed with CR0629's stories and the user-persona learning story if the release must shrink.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
