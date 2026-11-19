# BG1605: A run driven from a session started in another repository records no token stamp, so its report states no cost at all

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1605.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

### AC1: Plan warns when no token stamp can be taken

- **Given** a repository whose harness transcript store does not exist (no project folder for it, `SDLC_STUDIO_TRANSCRIPTS` unset)
- **When** `sprint plan --write` opens a run there
- **Then** the run still opens, and the plan prints a warning that no session token stamp could be taken, so the run's cost will read NOT MEASURED, and names `SDLC_STUDIO_TRANSCRIPTS` as the way to point the meter at the session's own store. Fails on: a silent plan, or a warning that names no remedy
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::CrossRepoMeterTests::test_plan_warns_when_no_token_stamp_can_be_taken

### AC2: A run in another repository is priced from the named store

- **Given** a second repository with no store of its own, and `SDLC_STUDIO_TRANSCRIPTS` pointing at a store holding the current session's transcript, which grows between the plan and the close
- **When** a run is planned and closed there
- **Then** the run carries an open and a closing stamp whose `source` is the transcript under the named store, and the report's Priced cost row carries a figure rather than NOT MEASURED. Fails on: no stamp, a stamp read from the second repository's absent store, or a cost row left NOT MEASURED
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::CrossRepoMeterTests::test_a_cross_repository_run_is_priced_from_the_named_store

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
