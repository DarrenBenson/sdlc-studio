# BG1197: Existing token-meter tests set SDLC_STUDIO_TRANSCRIPTS but leave the harness variables, so a suite run under Cursor, Copilot or OpenCode selects another meter and fails

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/conftest.py, .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py, changelog.d/BG1197.md
> **Evidence:** US0986 builder report, 2026-11-04, outside-the-unit item 1.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T11:14:12Z

## Summary

2026-11-04, US0986's build (run five). US0986 chooses the meter from `SDLC_STUDIO_HARNESS`, then from harness signals such as `CURSOR_AGENT`, `COPILOT_HOME`, OPENCODE and `OPENCODE_DB.` The token tests written before it point `SDLC_STUDIO_TRANSCRIPTS` at a fixture but never clear those variables, so they pass with nothing set or under CLAUDECODE=1, and a run inside another harness selects that harness's reader and fails.

## Steps to Reproduce

1. `CURSOR_AGENT=1 python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_run_state.py .claude/skills/sdlc-studio/scripts/tests/test_retro.py`.
2. Token tests that expect the Claude fixture reading fail.

## Proposed Fix

Clear the harness variables in one shared fixture the token tests use, named from `token_meters`' own signal list so a new harness is covered when it is added.

## Acceptance Criteria

- [ ] **AC1** The token tests pass with each harness signal set in the environment.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py

## Impact

A contributor working in Cursor, the harness CR0611 serves, sees a red suite that has nothing to do with their change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
