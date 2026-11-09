# US1140: The run's next action and a resume brief of at most 8k tokens are derived from disk alone

> **Status:** Ready
> **Delivers:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/resume_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py
> **Epic:** EP0302
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The run's next action and a resume brief of at most 8k tokens are derived from disk alone
**So that** CR0670 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given a fixture run in each of four states (a lane in flight; a landed unit with a QA brief and no APPROVE; every landed unit approved with a later wave unbriefed; every batch unit terminal), then `resume_brief.next_action(root)` returns one step per state by a fixed ladder in this order of precedence: await the in-flight lane, review the landed unit (or repair it after a REJECT), `sprint.py lane brief --units <that wave's unbriefed ids>`, then `sprint.py close` in its own fresh session. It reads only the tree and `sdlc-studio/.local/`, so two calls on one tree return the same step. Fails on: a state falling to a later rung while an earlier one holds, a step read from process state, or the close named while a batch unit is not terminal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_each_fixture_state_yields_its_rung_of_the_ladder
- **AC2:** Given an open run, then `resume_brief.at_wave_boundary(root)` is true only when every lane of the current wave is accepted and none is in flight, and otherwise false with the blocking unit named. Fails on: true with a lane in flight, or true with a landed unit still awaiting its verdict.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::NextActionTests::test_the_wave_boundary_holds_only_with_every_lane_accepted_and_none_in_flight
- **AC3:** Given an open run, then `resume_brief.build(root, agents=..., issues=...)` renders a markdown brief naming the run id and Sprint Goal, each batch unit's lane state (unbriefed, in flight, landed awaiting a verdict, accepted, or terminal), each in-flight lane's agent id where the caller supplied one, each pending QA brief by path and each pending verdict, the run's rulings from the run state's `rulings`, the known issues (the caller's, and each open bug or CR whose `Raised-in-batch` names the run), whether the run stands at a wave boundary, and the next action from AC1. Fails on: a batch unit absent from the brief, a pending QA brief or verdict not named, or an in-flight lane listed without the agent id the caller supplied.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_the_brief_names_every_unit_and_each_pending_item
- **AC4:** Given a brief whose estimate (characters divided by four, rounded up, the rule the module states) exceeds 8,000 tokens, then `build` raises an error naming the estimate and the budget instead of returning a truncated brief; given a 30-unit fixture batch with ten rulings, the brief fits the budget. Fails on: a silently truncated brief, an over-budget brief returned, or the 30-unit brief refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_an_over_budget_brief_is_refused_and_a_thirty_unit_brief_fits
- **AC5:** Given a built brief, then `resume_brief.parse(text)` returns the run id and next action it was built with, and a schema-3 unit spelt `US-01M6XQJF` in one place and `US01M6XQJF` in another is read as one unit under `sdlc_md.norm_id`. Fails on: a round trip that changes the next action, or the two spellings read as two units (the BG1302 shape).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume_brief.py::ResumeBriefTests::test_the_brief_round_trips_and_a_schema3_id_is_one_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
