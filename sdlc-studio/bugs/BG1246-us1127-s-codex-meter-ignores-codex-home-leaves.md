# BG1246: US1127's Codex meter ignores `CODEX_HOME`, leaves its workspace boundary unpinned, and its AC3 test names a timeout mutant it cannot kill

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py
> **Evidence:** run seven (RUN-01M6RAP7) US1127 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:25Z

## Summary

Run seven, US1127 round 1 (APPROVE, non-blocking). (1) `CODEX_HOME` is not honoured: `codex_home` reads only HOME (`meter_codex.py:51-53`). Executed with `CODEX_HOME` naming a populated store and no `~/.codex`: tokens None, `no Codex state store sits at <HOME>/.codex/state_5.sqlite`. That is a named None, not a zero, so AC3 holds, but a session that relocates its home is never metered, and one that also has a stale `~/.codex` holding threads for the workspace reads that store's frozen total. (2) The workspace boundary is unpinned: replacing `startswith(workspace.rstrip(os.sep) + os.sep)` with `startswith(workspace)` (`meter_codex.py:133`) passes the whole module, so a sibling thread in `/x/repo-old` could be booked to `/x/repo` with the suite green; HEAD is right (`_within("/a/repo-x", "/a/repo")` is False). (3) AC3's test docstring (`test_meter_codex.py:202`) names "a lock waited on for SQLite's default 5 s", but dropping `timeout=TIMEOUT_SECONDS` from the store's only open (`meter_codex.py:118`) passes the test (5.4 s instead of 0.5 s), because it patches the constant (line 256) and asserts the constant (line 261), never the wait. (4) Reading a closed WAL store creates a 0-byte `state_5.sqlite-wal` and a `state_5.sqlite-shm` and leaves them. That is SQLite's normal behaviour for a `mode=ro` reader and the store's bytes are unchanged, but "never opened for writing" (the `meter_codex.py` docstring and `reference-sprint.md`) reads as if a read leaves `~/.codex` untouched.

## Steps to Reproduce

1. Point `CODEX_HOME` at a populated scratch store with no `.codex` under a fake HOME, and read the meter: tokens None, naming `<HOME>/.codex`. 2. Apply the `startswith(workspace)` and dropped-timeout mutants in a scratch copy and run `pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py`: all pass.

## Proposed Fix

Resolve the store from `CODEX_HOME` when set, else `~/.codex`, and pin both. Add a sibling-prefix thread (`/x/repo-old` against `/x/repo`) to AC1's fixture. Make AC3's test hold a write lock and assert the read returns within the bound, or drop that mutant from its docstring. Reword the docstring and `reference-sprint.md`: the store's bytes are never written, though SQLite may create its `-wal` and `-shm` beside it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US1127 round 1 (APPROVE, non-blocking).
- [ ] **AC2** The proposed fix lands, pinned by a test: Resolve the store from `CODEX_HOME` when set, else `~/.codex`, and pin both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
