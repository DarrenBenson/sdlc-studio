# US0927: A sprint plan names the PRD outcome or persona its goal serves, and flags a goal that serves none

> **Status:** In Progress
> **Delivers:** CR0594
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/core/prd.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py, changelog.d/US0927.md
> **Epic:** EP0264
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As** Maya Okafor, approving a sprint plan
**I want** the plan to tell me which PRD outcome or persona the Sprint Goal serves, and to say plainly when it serves none
**So that** a run cannot drift into building its own machinery without my seeing it at the one approval I give - End goal 1, "Ship real features through a disciplined lifecycle (spec -> story -> implement -> verify), not ad-hoc edits"

## Acceptance Criteria

- **AC1:** Given a fixture whose `sdlc-studio/prd.md` has an `## Outcomes` section listing `- **O1:** ...` and `- **O2:** ...` and whose `sdlc-studio/personas/` holds a Primary card for Maya Okafor, when `sprint.py plan --worklist <file> --sprint-goal "<goal>" --serves O2 --format json` runs, then the JSON carries a `goal_trace` naming O2 with O2's text read from the PRD and `flagged: false`, and the text form prints `goal serves: O2 - <that text>`; a trace that echoes the flag without reading the PRD fails it, because the outcome text is asserted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py::GoalTraceTests::test_serves_names_a_prd_outcome_with_its_text
- **AC2:** Given the same fixture and no `--serves`, when the goal sentence itself names `Maya` (or `Maya Okafor`) or `O1` as a whole word, then `goal_trace` names Maya Okafor (Primary) or O1 respectively; a trace that reads only `--serves` fails it, and a goal containing `Mayan` traces to nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py::GoalTraceTests::test_a_goal_that_names_a_persona_or_outcome_is_traced
- **AC3:** Given a goal that names no outcome or persona and no `--serves`, or `--serves O9` where the PRD lists no O9, when the plan runs, then it prints `goal serves: NONE` naming the outcomes and personas the goal could serve (and, for O9, that the PRD lists no such outcome), and its exit code and the batch written to `sprint-plan.json` are identical to the same plan with a traced goal - a flag, never a refusal; an implementation that exits non-zero or omits the line fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py::GoalTraceTests::test_a_goal_serving_none_is_flagged_and_never_refused
- **AC4:** Given a goal traced only to a persona whose card's `Cast role` is Negative, when the plan runs, then it is flagged as serving a persona the product declines to design for, in the same advisory way; an implementation that counts any named persona as served fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py::GoalTraceTests::test_a_goal_serving_only_the_negative_persona_is_flagged
- **AC5:** Given a project whose `prd.md` has no `## Outcomes` section and which has no persona cards, when the plan runs, then no trace line is printed and no `goal_trace` is recorded - a line that fires on every plan in such a project would never be read - and `templates/core/prd.md` carries an `## Outcomes` section in the grammar AC1 parses, so a consuming project's PRD can be traced; an implementation that always prints NONE fails it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal_trace.py::GoalTraceTests::test_nothing_to_trace_against_prints_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-25 | Product seat | Groomed from CR0594's refinement: user story and criteria authored |
