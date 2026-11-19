# BG1282: `COPILOT_HOME` and `OPENCODE_DB`, user configuration variables, count as harness signals, so a Claude Code user who exports either gets no token reading

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py, changelog.d/BG1282.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:06:56Z

## Summary

`COPILOT_HOME` and `OPENCODE_DB` are user configuration variables, yet they count as harness signals. A Claude Code user who exports either in their shell profile gets 'the environment signals 2 harnesses' and no token reading on every run. The reason names the `SDLC_STUDIO_HARNESS` workaround. This is per spec (BG1205 AC9, CR0611).

## Steps to Reproduce

`token_meters.select(repo`, None, {CLAUDECODE:1, `COPILOT_HOME`:<tmp>}) -> {'harness': None, 'candidates': ['claude','copilot'], ...}; the same with `OPENCODE_DB.`

## Proposed Fix

Treat config variables as weaker than a running-process signal: when CLAUDECODE, `CURSOR_AGENT`, OPENCODE or `CODEX_THREAD_ID` is set, ignore `COPILOT_HOME` and `OPENCODE_DB.`

## Acceptance Criteria

- [ ] **AC1** Given an environment with `CLAUDECODE` set beside `COPILOT_HOME`, or beside `OPENCODE_DB`, when `token_meters.select` runs, then it selects Claude and takes a reading. Fails on: `harness: None` with two candidates and no token reading.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_a_config_variable_yields_to_a_running_process_signal
- [ ] **AC2** Given an environment where `COPILOT_HOME` or `OPENCODE_DB` is the only harness variable set, when `token_meters.select` runs, then it still selects Copilot or OpenCode. Fails on: a configuration variable ignored outright.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::HarnessSelectionTests::test_a_config_variable_alone_still_selects_its_harness

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
