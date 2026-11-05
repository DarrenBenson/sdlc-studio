# US1117: sprint lane return --agent prices a lane from its builder's own transcript, and the report's unit row shows that priced cost

> **Status:** Ready
> **Delivers:** CR0661
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, changelog.d/US1117.md
> **Epic:** EP0298
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint lane return --agent prices a lane from its builder's own transcript, and the report's unit row shows that priced cost
**So that** a run can see what each unit cost in the priced figure its headline uses

## Acceptance Criteria

- **AC1:** Given an open run and a fixture subagent transcript `agent-<id>.jsonl` in which one message's usage is logged on two lines, when `sprint.py lane return --units <unit> --agent <id>` runs, then the unit's delegated record carries that transcript's priced cost and its components, each message counted once and weighted by `TOKEN_WEIGHTS`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_the_agent_transcript_prices_the_lane_once_per_message
- **AC2:** Given a build and a repair returned for one unit with different agents, then the unit's row on the sprint report shows the summed priced cost labelled priced, and the report states the run's priced cost per delivered point
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_a_repair_adds_to_the_unit_priced_row
- **AC3:** Given an `--agent` that names no transcript in the session, then the return still completes, records no priced figure, and warns naming the agent id and the directory searched; with the transcript present no warning prints
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_an_unknown_agent_warns_and_records_no_priced_cost

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Created via `new` (deterministic) |
