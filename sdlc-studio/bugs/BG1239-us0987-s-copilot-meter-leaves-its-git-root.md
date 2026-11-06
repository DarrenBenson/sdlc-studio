# BG1239: US0987's Copilot meter leaves its git-root-over-cwd preference unpinned and counts `includes_subagents: False` on trust

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_copilot.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py
> **Evidence:** run seven (RUN-01M6RAP7) US0987 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:35:36Z

## Summary

Run seven, US0987 round 1 (APPROVE, two non-blocking findings). (1) The git-root-over-cwd preference has no test that can fail: the mutant `context.get("cwd") or context.get("gitRoot")` at `meter_copilot.py:84` passes the whole module (5 tests, 14 subtests), because the test's `start()` (`test_meter_copilot.py:79`) writes `cwd` equal to `gitRoot`, while the real resumed capture the fixtures derive from recorded `cwd` as `gitRoot`/`sdlc-studio/.local/copilot-scratch`. Probed in isolation: a session with `gitRoot`=repo and `cwd`=repo/sub is read today (9 tokens, 3 cache reads) and is lost under the mutant, so `reference-sprint.md:624` ("records this repo as its git root (or, outside git, its directory)") stands unpinned. (2) `includes_subagents: False` (`meter_copilot.py:223`) is unverifiable: both real 2026-11-06 sessions ran the main agent alone (`agentMetrics` names only `main`), so whether the shutdown's `modelMetrics` folds subagent calls in is settled by no capture.

## Steps to Reproduce

1. In a scratch copy, change `meter_copilot.py:84` to prefer `cwd` over `gitRoot`. 2. Run `pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_copilot.py`: every test passes. 3. Feed the meter a session whose `gitRoot` is the repo and whose `cwd` is a subdirectory of it: the shipped code reads 9 tokens, the mutant none.

## Proposed Fix

Add a fixture session whose `cwd` sits below its `gitRoot` and assert it is booked to the repo, so the mutant fails. Capture one real Copilot session that delegates to a subagent and settle whether `modelMetrics` includes its calls; until then, state the assumption in the `meter_copilot.py` docstring and `reference-sprint.md` rather than recording `includes_subagents: False` as observed.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US0987 round 1 (APPROVE, two non-blocking findings).
- [ ] **AC2** The proposed fix lands, pinned by a test: Add a fixture session whose `cwd` sits below its `gitRoot` and assert it is booked to the repo, so the mutant fails.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
