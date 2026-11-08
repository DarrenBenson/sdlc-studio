# BG1249: The suite's root `conftest.py` isolates neither `HOME` nor `XDG_DATA_HOME`, so suite tests and reviewer mutant runs open the operator's live harness stores

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** conftest.py, .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py, changelog.d/BG1249.md
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

- **AC1:** Given a pytest session under the root `conftest.py`, then `HOME`, `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` each name a directory under the session's private `TMPDIR`, and `CODEX_HOME`, `COPILOT_HOME`, `CLAUDE_CONFIG_DIR` and `OPENCODE_DB` are unset, in the main process and in an xdist worker. Fails on: a session that leaves `HOME` as the operator's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_the_session_home_is_private
  - **Verified:** yes (2026-11-08)
- **AC2:** Given the store paths the token-meter selection's step 3 probes for Codex, Copilot and OpenCode, then each resolves inside the session's private directory and none under the operator's home, read from the passwd entry (`pwd.getpwuid(os.getuid()).pw_dir`) rather than `$HOME`. Fails on: a probe that resolves the operator's `~/.codex`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_a_step_three_probe_stays_private
  - **Verified:** yes (2026-11-08)
- **AC3:** Given a fixture repository that commits with no identity of its own, then the commit succeeds under the private home's test identity, and `pytest_unconfigure` restores `HOME` and every variable the session changed or unset to the value it had before. Fails on: a commit refused for want of an identity, or `HOME` left pointing at the private directory after the session.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_a_fixture_commit_has_an_identity .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py::PrivateHomeTests::test_unconfigure_restores_what_it_changed
  - **Verified:** yes (2026-11-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Groomed for the 6.3.0 release bar (D0427): criteria with Verify lines; the changelog fragment joins Affects |
