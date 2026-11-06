# CR-0667: A lane runs headless in any supported CLI harness and is priced from the usage that CLI prints

> **Status:** In Progress
> **Decomposed-into:** EP0299
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py
> **Evidence:** RFC0062 Phase 1; run six's transcripts and the 2026-11-06 capture of one headless session per CLI harness.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:17:49Z

## Summary

Only Claude Code prices a lane from its builder's own transcript. Every supported CLI prints usage in headless JSON (captured 2026-11-06): claude -p --output-format json, cursor-agent -p --output-format json, codex exec --json, copilot -p --output-format json and opencode run --format json. They disagree on what input means: Codex and Copilot count cached tokens inside input, Claude Code and OpenCode count them apart. A launcher that runs a lane's brief headless and records that usage prices lanes in every harness, and lets a lane use another harness or a cheaper model.

## Impact

A sprint driven from Cursor, Copilot, Codex or OpenCode has no per-lane cost, and no lane can be run on another harness or model.

## Acceptance Criteria

- [ ] sprint.py lane run --harness claude|cursor|codex|copilot|opencode --units <id> runs the lane's brief headless in the lane's worktree and records the session id, model and usage on the lane
- [ ] Usage is normalised to one basis (input without cache, cache read, cache write, output with reasoning inside it); Codex's and Copilot's input is split from its cached part and never counted twice; each harness's normaliser is pinned by a fixture taken from a real captured session
- [ ] A CLI that exits non-zero, prints no usage, or prints a line that does not parse leaves the lane recorded as unmetered with the reason, and the lane's work is still returned
- [ ] Where the harness reports its own total (Claude Code's `total_cost_usd`, Copilot's session accounting), the recorded figure is checked against it and a disagreement above 5% is named
- [ ] The lane brief and reference-sprint.md say how a harness without subagents runs its lanes this way

## Recommendation

One normaliser module per harness beside the existing meter readers, shared with the benchmark runner.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
