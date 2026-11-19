# BG1605: A run driven from a session started in another repository records no token stamp, so its report states no cost at all

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG-METER.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** the website's RUN-01M7R7KN, 2026-11-19: orchestrator; its run-state holds no stamps, while run seventeen's 18 stamps in the same session name this repository's project folder as their source
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:50:22Z

## Summary

`run_state.stamp_tokens` reads the session meter with `session_tokens(repo_root)`, which looks for the session transcript under the harness project folder derived from the run's own repository root. When the orchestrator drives a run in a second repository from a session started in the first (the website's run, driven from this repository's session), that folder does not exist, every stamp returns None, and the run carries no `session_token_stamps` and no baseline. `sprint close` then reports every token and dollar row NOT MEASURED, and the retro says 'not attributable', although every main-thread and subagent transcript for the run is on disk under the first repository's project folder.

## Steps to Reproduce

Start a session in repository A, then `sprint plan`, deliver and `sprint close --root <repository B>`: B's run-state has `session_token_stamps: []` and `session_token_baseline: null`, and its report's Priced cost and Dollar cost rows read NOT MEASURED.

## Proposed Fix

Resolve the session transcript from the harness's own session (its id or transcript path, as the stamp's `source` already records for a same-repository run) rather than from the run's repository root, or accept `--transcripts-dir` on `sprint plan` and `sprint close` and say at plan time when no stamp could be taken, so a run is never opened unpriced without a warning.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `run_state.stamp_tokens` reads the session meter with `session_tokens(repo_root)`, which looks for the session transcript under the harness project folder...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Start a session in repository A, then `sprint plan`, deliver and `sprint close --root <repository B>`: B's run-state has `session_token_stamps: []` and...
- [ ] **AC3** The proposed fix lands, pinned by a test: Resolve the session transcript from the harness's own session (its id or transcript path, as the stamp's `source` already records for a same-repository run)...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
