# BG1249: The suite's root `conftest.py` isolates neither `HOME` nor `XDG_DATA_HOME`, so suite tests and reviewer mutant runs open the operator's live harness stores

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** conftest.py, .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py
> **Evidence:** run seven (RUN-01M6RAP7) US0988 review rounds 1 and 2, and the orchestrator's friction log (F10)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:37:10Z

## Summary

Run seven, US0988 review rounds 1 and 2 (tagged pre-existing) and the orchestrator's friction log (F10). The root `conftest.py` clears the variables `token_meters.selection_variables()` names (`conftest.py:56-75`) and gives the session a private `TMPDIR` (`pytest_configure`, :105-114), but leaves `HOME` and `XDG_DATA_HOME` as the operator's, so a test that reaches the token-meter selection's step 3 probes the real `~/.codex`, `~/.copilot` and `~/.local/share/opencode` stores. Evidence: a run of the OpenCode and token-meter modules on an unmutated HEAD copy touched both live `-shm` files; under a US0988 review mutant (a plain `sqlite3.connect` in `store()`) one suite run checkpointed this machine's `~/.local/share/opencode/opencode.db` (262144 to 303104 bytes, its `-wal` and `-shm` removed, at 12:47:40) with every test green. Its content was verified intact against a prior copy, so no data was lost, but a mutant that wrote would have written to the operator's store. Only US0988's AC2 fixture fakes `HOME` and scrubs `OPENCODE_DB` and `XDG_DATA_HOME` (`test_meter_opencode.py:175-183`). Related, not the same: BG1207 (the harness scrub lives only in the root conftest, so unittest runs miss it).

## Steps to Reproduce

1. Note the modification times of `~/.local/share/opencode/opencode.db-shm` and `~/.codex/state_5.sqlite-shm`. 2. Run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py`. 3. Both times have moved.

## Proposed Fix

In `pytest_configure`, point `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` at directories under the session's private directory, unset `CODEX_HOME`, `COPILOT_HOME`, `CLAUDE_CONFIG_DIR` and `OPENCODE_DB`, and restore them all in `pytest_unconfigure`. Seed the private home with a `.gitconfig` carrying a test identity, since fixture commits read it from `HOME` today, and keep the `GIT_CONFIG_COUNT` maintenance pin. Pin it with a test asserting that a step-3 probe resolves inside the private directory and never under the operator's home.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US0988 review rounds 1 and 2 (tagged pre-existing) and the orchestrator's friction log (F10).
- [ ] **AC2** The proposed fix lands, pinned by a test: In `pytest_configure`, point `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` at directories under the session's private...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
