# US1124: sprint cost --anatomy breaks a run's spend down by role and names the tool outputs that drove it

> **Status:** Ready
> **Delivers:** CR0666
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md, changelog.d/US1124.md
> **Epic:** EP0299
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint cost --anatomy breaks a run's spend down by role and names the tool outputs that drove it
**So that** a run's cost drivers are visible without hand analysis of transcripts

## Acceptance Criteria

- **AC1:** Given a fixture session with a main transcript and subagent transcripts that `lane return --agent` and `lane accept` recorded, when `sprint.py cost --anatomy` runs, then it prints per role (orchestrator, builder, reviewer, repair, other) the agents, calls, priced tokens and share, the cache-read, cache-write and output split, the first call's context and the average context per call, each message counted once at its largest usage. Fails on: a message counted at its first, partial usage record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_per_role_rows_from_lane_records
- **AC2:** Given the same fixture, then it names the ten tool outputs that cost most, each costed as its size times the later calls that re-read it, with the command or file that produced it. Fails on: outputs ranked by size alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_heaviest_tool_outputs_are_named
- **AC3:** Given a subagent no lane or review record names, then it is counted under other, and its prompt text is never used to guess its role. Fails on: a role guessed from prompt wording
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_an_unrecorded_agent_is_other
- **AC4:** Given a harness reading with no per-call context, then the context columns print as not available, never 0. Fails on: a missing context printed as zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_no_per_call_context_is_not_available

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
