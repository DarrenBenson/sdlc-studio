# BG0326: Remote-aware id allocation silently degrades to local-only when the git query fails, minting the collision it exists to

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

`remote_ids` returns ([], False) identically for 'no origin' (silence correct) and 'origin exists but the query failed' (git absent, timeout, unfetched ref), and `allocate_number` then quietly allocates from local ids only; artifact.py, the mandated creation path, surfaces nothing, and text-mode output prints only the bare id - so a failed remote read can re-issue an id origin already holds, the LL0002 cross-repo collision class, from the one tool whose job is preventing it.

## Steps to Reproduce

Evidence (`remote_ids()` lines 130-146; `allocate_number()` lines 102-112; `cmd_allocate` lines 176-202; consumed at artifact.py:729): Lines 143-146 collapse failure and absence into one value; lines 109-111 ignore availability silently; line 183's only warning path requires `remote_available` True; AGENTS.md sells 'id allocation is remote-aware'.

## Proposed Fix

Return a tri-state from `remote_ids` (no-origin / scanned / failed) and, when an origin exists but the scan failed, print a loud warning in every output mode and refuse allocation under a --strict flag used by sprint pre-flight.

## Acceptance Criteria

### AC1: a failed remote scan is distinguished from no origin

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::RemoteScanHonestyTests::test_failed_scan_is_distinguished_from_no_origin`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
