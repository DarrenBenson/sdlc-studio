# BG1383: Two more group-kill helpers duplicate verify_ac's, one closure in mutation.py and one in verify_ac._run_phase

> **Status:** Won't Fix
> **Supersedes:** BG1419
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_group_kill_shared.py, changelog.d/BG1383.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane reaper builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:06:27Z

## Summary

mutation.py (around line 1014) and `verify_ac.py` `_run_phase` (around line 2381) each carry their own `os.killpg` SIGKILL logic instead of calling `_kill_group`, so the SIGTERM-first grace and reaping fixed in `_kill_group` do not reach them.

## Steps to Reproduce

grep -n killpg in mutation.py and `verify_ac.py`: three independent kill paths.

## Proposed Fix

Route both through `_kill_group`.

## Acceptance Criteria

- [ ] **AC1** Given a mutation probe or a `_run_phase` child that ignores SIGTERM, when it times out, then the shared `_kill_group` ends it with SIGTERM first and then SIGKILL. Fails on: either site sending SIGKILL directly through its own copy.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_group_kill_shared.py::GroupKillSharedTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because it is the residue of a fix that has already shipped. Duplicate group-kill closures left after the shipped fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
