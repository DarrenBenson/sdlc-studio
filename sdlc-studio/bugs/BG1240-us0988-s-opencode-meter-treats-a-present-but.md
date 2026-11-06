# BG1240: US0988's OpenCode meter treats a present but unreadable store as absent, against the token-meter contract, and its docstring says a read leaves the write-ahead log alone

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py
> **Evidence:** run seven (RUN-01M6RAP7) US0988 review rounds 1 and 2
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:35:44Z

## Summary

Run seven, US0988 rounds 1 and 2 (round 2 APPROVE; both findings re-executed in round 2 and still open). (1) `store()` catches `sqlite3.Error` and returns None (`meter_opencode.py:237-238`), so a database that is present but cannot be read is never a step-3 candidate, against the contract in `token_meters.py:111-113` that a probe which cannot read a store "is reported as a candidate", which the Codex and Copilot probes keep by raising. Executed: a present default database at mode 000 gives None, and with no signal the selection falls to Claude by default, so the run is metered by the wrong harness with no warning. (2) The module docstring (`meter_opencode.py:25-26`) says a read writes neither the database "nor its write-ahead log" and touches only the `-shm`, but re-executed, `read_db` on a closed WAL database creates a 0-byte `opencode.db-wal` beside a new 32768-byte `-shm`.

## Steps to Reproduce

1. Copy an OpenCode database into a scratch `XDG_DATA_HOME`, `chmod 000` it, clear every harness variable and run the token-meter selection: Claude is chosen and OpenCode is never named as a candidate. 2. Close a WAL database cleanly, call `read_db` on it and list its directory: a 0-byte `opencode.db-wal` and a 32768-byte `opencode.db-shm` now exist.

## Proposed Fix

Have `store()` raise (or return a candidate marked unreadable) on `sqlite3.Error` for a file that exists, as the Codex and Copilot probes do, and pin it with a mode-000 fixture asserting OpenCode is reported as a candidate. Correct the docstring: a read-only open of a WAL database may create the `-wal` and `-shm` files beside it but never writes the database's bytes.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US0988 rounds 1 and 2 (round 2 APPROVE; both findings re-executed in round 2 and still open).
- [ ] **AC2** The proposed fix lands, pinned by a test: Have `store()` raise (or return a candidate marked unreadable) on `sqlite3.Error` for a file that exists, as the Codex and Copilot probes do, and pin it with a...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
