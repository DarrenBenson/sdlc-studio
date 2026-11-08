# BG1282: `COPILOT_HOME` and `OPENCODE_DB`, user configuration variables, count as harness signals, so a Claude Code user who exports either gets no token reading

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py
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

- [ ] **AC1** The behaviour described is corrected: `COPILOT_HOME` and `OPENCODE_DB` are user configuration variables, yet they count as harness signals.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: `token_meters.select(repo`, None, {CLAUDECODE:1, `COPILOT_HOME`:<tmp>}) -> {'harness': None, 'candidates': ['claude','copilot'], ...}; the same with...
- [ ] **AC3** The proposed fix lands, pinned by a test: Treat config variables as weaker than a running-process signal: when CLAUDECODE, `CURSOR_AGENT`, OPENCODE or `CODEX_THREAD_ID` is set, ignore `COPILOT_HOME`...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
