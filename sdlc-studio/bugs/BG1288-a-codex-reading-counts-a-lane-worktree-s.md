# BG1288: A Codex reading counts a lane worktree's own `codex exec` thread but says it holds no subagent spend, so the report adds the lane's delegated total a second time

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py, changelog.d/BG1288.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:08:35Z

## Summary

A Codex reading sums every thread whose cwd is the workspace or under it, and lane worktrees sit under the workspace (`lanes.RUN_WORKTREES` = sdlc-studio/.local/worktrees). So a `sprint lane run --harness codex` lane's own `codex exec` thread is already in the run's meter delta. But the reading says `includes_subagents`=False unless a `thread_spawn_edges` child exists. The report then adds the lane's delegated harness-output total on top. The lane's spend is counted twice in the Estimates Tokens actual (which drives cost per point and the ratio) and in the cost section's `tokens_total.` The Priced cost headline, which is meter-only, is unaffected.

## Steps to Reproduce

python3 rel63/legs/scratch-a/`codex_lane.py` <tmp> <scripts> (temp HOME/`CODEX_HOME`, `SDLC_STUDIO_HARNESS`=codex; orchestrator thread at root grows 11,000; lane thread at root/sdlc-studio/.local/worktrees/lane-us1 spends 44,000; one delegated record of 44,000) -> 'close reading: tokens 66000 subagents flag False' / 'meter delta: 55000 `includes_subagents`: False' / '`delegated_total`: 44000' / 'report Tokens actual (`_run_tokens_actual)`: (99000, 1)'. The true spend is 55,000.

## Proposed Fix

In `meter_codex`, set `includes_subagents` True whenever any counted thread's cwd is not the workspace itself (a worktree or subdirectory thread is delegated spend already in the reading). Or exclude cwd under sdlc-studio/.local/worktrees from the sum, so lanes are counted once, through their delegated records. Pin it with a test of a lane-worktree thread plus a delegated record.

## Acceptance Criteria

- **AC1:** Given a Codex store holding a workspace-root thread that grows 11,000 tokens and a thread whose cwd is a lane worktree under `sdlc-studio/.local/worktrees/` that spends 44,000, and one delegated lane record of that 44,000, when the run's Tokens actual is derived through `sprint_report`, then it reads 55,000, the lane counted once. Fails on: `includes_subagents` left False for a reading that holds a worktree thread (the observed 99,000).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_a_lane_worktree_thread_is_counted_once
- **AC2:** Given a Codex store whose only counted threads have the workspace itself as their cwd and no spawned child, then the reading's `includes_subagents` is False, as before. Fails on: a fix that sets the flag for every reading.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_a_root_only_reading_holds_no_subagent_spend

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Criteria with Verify lines for the 6.3.0 cut (D0428); the changelog fragment joins Affects |
