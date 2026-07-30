# BG0339: check_neutrality silently reports a tracked file it could not read as clean, the exact silent-pass its own ls-files path

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/check_neutrality.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_d141ccb5

## Summary

check() swallows OSError per file and moves on, so a tracked file the guard could not read at all is scanned as if empty and main() exits 0 with 'no blocklisted project names in tracked files'; `_tracked_text_files` three lines above applies LL0008 (fail loud) to the listing failure with an explicit comment and SystemExit, but the per-file read failure gets the forbidden silent clean-pass.

## Steps to Reproduce

Evidence (check(), lines 86-89 ('except OSError: continue')): Confirmed at tools/`check_neutrality.py` 86-89: `read_text` uses errors='replace' so decode faults are already handled, meaning the except OSError catches only files never read, which are then reported clean.

## Proposed Fix

Collect unreadable files and fail loud (SystemExit naming them), mirroring the LL0008 treatment already applied in `_tracked_text_files`, instead of continue.

## Acceptance Criteria

### AC1: a tracked file the guard cannot read is reported, never counted clean

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest tools/tests/test_check_neutrality.py::UnreadableFileTests, written red before the fix and green after
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Filed |
| 2026-07-28 | Claude Fable 5 | Delivered in RUN-01KYJZGZ; acceptance criteria authored at review against the tests that landed |
