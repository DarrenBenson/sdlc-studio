# US1126: sprint lane run runs a lane's brief headless in any supported CLI and prices the lane from the usage it prints

> **Status:** Ready
> **Delivers:** CR0667
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md, changelog.d/US1126.md
> **Epic:** EP0299
> **Points:** 5
> **Depends on:** US1125
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint lane run runs a lane's brief headless in any supported CLI and prices the lane from the usage it prints
**So that** a sprint driven from any supported CLI prices each lane, and a lane can run on another harness or model

## Acceptance Criteria

- **AC1:** Given `sprint.py lane run --harness <h> --units <id>` for each of claude, cursor, codex, copilot and opencode, then it runs that harness's headless command with the lane's brief in the lane's worktree under a timeout, passing `--model` through when given; a fake CLI on PATH stands in for each harness in the test. Fails on: the command run in the main tree rather than the worktree
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_each_harness_runs_its_headless_command_in_the_worktree
- **AC2:** Given a run that prints usage, then the lane record holds the session id, model and usage normalised by `lib/harness_usage.py`, and `lane return` prices the lane from it. Fails on: the lane priced from the orchestrator's own transcript
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_the_lane_is_priced_from_the_recorded_usage
- **AC3:** Given a CLI that exits non-zero or prints no usage, then the lane is recorded as unmetered with the reason, and its staged work is still returned. Fails on: a silent CLI recorded as zero tokens, or its work discarded
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_failed_or_silent_cli_leaves_the_lane_unmetered
- **AC4:** Given `reference-agent-prompt-template.md`, then it says how a harness without subagents runs each lane with `lane run`, one fresh session per lane. Fails on: the template naming only the subagent route
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_the_template_names_lane_run_for_a_harness_without_subagents

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
