# BG0322: pvd sync --mode symlink reports 'synced' and exits 0 after creating a dangling link to a nonexistent master

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/pvd.py, .claude/skills/sdlc-studio/scripts/tests/test_pvd.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Symlink mode never verifies the master PVD exists before linking (non-strict resolve, `symlink_to` succeeds on any path), so a mistyped --master yields a dangling symlink while the tool prints {'action': 'synced'} and returns 0; copy mode fails loud on the same input, so the mode designated for production is the one reporting success it did not achieve.

## Steps to Reproduce

Evidence (sync(), lines 44-63; `cmd_sync()`, lines 92-95): Lines 58-59 link with no existence check; reproduced: sync against `NO_SUCH_FILE.md` printed synced, exited 0, left a dangling link; contrast drift() lines 70-71, which refuses a vacuous in-sync verdict on an unreadable master.

## Proposed Fix

In sync(), refuse with exit 1 when the master path does not exist (mirroring drift()'s guard) before creating the link or copy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
