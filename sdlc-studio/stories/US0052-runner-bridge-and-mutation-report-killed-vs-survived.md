# US0052: Runner bridge and mutation report: killed vs survived per mutation, honest un-checked degrade

> **Status:** Ready
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Epic:** EP0011
> **Persona:** Sam (QA amigo)
> **Story Points:** 3
> **Depends on:** US0051

## User Story

**As a** QA gate consumer
**I want** each applied mutation re-run against the mapped tests, with a per-mutation killed/survived verdict persisted to a report
**So that** a test that stays green while its feature is broken becomes a visible finding instead of a silent false pass

## Design (settles RFC-0022 D5 within the accepted direction)

- **Verdicts:** `killed` (the test command failed - the test pins the behaviour), `survived`
  (the test command passed - a finding), `error` (the runner itself broke - reported, neither
  killed nor survived).
- **Report home (D5):** `sdlc-studio/.local/mutation-report.json` - `generated_at`, targets,
  per-mutation records `{file, line, class, occurrence, verdict}`, `unchecked` list, and a
  summary `{applied, killed, survived, errors, truncated}`. Same shape in text output.
- **Exit semantics:** non-zero when any mutation survived (a finding is never a silent pass);
  zero otherwise. `error` records are surfaced but do not fake a kill.

## Acceptance Criteria

### AC1: a vacuous test survives, a load-bearing test kills

- **Given** a target with one test that asserts the mutated behaviour and one that asserts nothing
- **When** the bridge runs the mutation set
- **Then** the load-bearing test's mutations report killed and the vacuous test's report survived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::BridgeTests::test_vacuous_survives_loadbearing_kills

### AC2: the report is written with verdicts and summary

- **Given** a completed run
- **When** the report is read back
- **Then** it carries per-mutation verdicts, the un-checked list, and a summary whose counts equal the records
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::BridgeTests::test_report_shape_and_counts

### AC3: survivors exit non-zero

- **Given** a run with at least one survived mutation
- **When** the CLI returns
- **Then** the exit code is non-zero and the survivor is named in the output
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::BridgeTests::test_survivor_exits_nonzero

### AC4: a runner error is reported, never counted as killed

- **Given** a test command that itself crashes (not a test failure)
- **When** the run completes
- **Then** the mutation records verdict error and the summary separates it from killed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::BridgeTests::test_runner_error_not_a_kill

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
| 2026-07-04 | claude | Authored at design: D5 settled per accepted RFC-0022; points + ACs + Verify lines |
