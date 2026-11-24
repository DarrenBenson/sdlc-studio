# BG1712: Nine whole-file rewrites of tracked workspace files still truncate in place instead of going through sdlc_md.atomic_write, so an interrupted write can leave the file half-written

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** BG1532 round-one REJECT (verdict 9b6b9edda357-80d11a05) and the round-two repair's NOT_YET_MOVED list
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T21:28:13Z

## Summary

The shared-file write sweep (`test_confinement.py` SharedFileWriteSweepTests) lists nine whole-file rewrites of tracked workspace files on its separate `NOT_YET_MOVED` list, and sdlc-studio/trd.md names them as outside the atomic-write guarantee: artifact.py `_WriteJournal.rollback`, `close_owed.py` `stamp_baseline`, `command_audit.py` `file_coverage_findings`, refine.py `_fill_user_story`, retro.py `cmd_cost_baseline`, sprint.py `record_charter_review`, `triage_noise.py` `_append_finding`, and `verify_ac.py` `revert_check` (twice). Each truncates the file and writes it whole, so a process killed mid-write leaves a committed artefact (a story, a CR, the charter, a baseline) truncated. Found when BG1532's round-one review widened the sweep to `write_bytes` and open.

## Steps to Reproduce

Read `NOT_YET_MOVED` in .claude/skills/sdlc-studio/scripts/tests/`test_confinement.py` and the shared-file exceptions in sdlc-studio/trd.md; each named site calls `write_text` or `write_bytes` on a tracked workspace path.

## Proposed Fix

Move each site onto `sdlc_md.atomic_write` (keeping its encoding and newline), empty `NOT_YET_MOVED`, and drop the not-yet-moved bullet from the TRD's exception list.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The shared-file write sweep (`test_confinement.py` SharedFileWriteSweepTests) lists nine whole-file rewrites of tracked workspace files on its separate...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read `NOT_YET_MOVED` in .claude/skills/sdlc-studio/scripts/tests/`test_confinement.py` and the shared-file exceptions in sdlc-studio/trd.md; each named site...
- [ ] **AC3** The proposed fix lands, pinned by a test: Move each site onto `sdlc_md.atomic_write` (keeping its encoding and newline), empty `NOT_YET_MOVED`, and drop the not-yet-moved bullet from the TRD's...

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. Nine non-atomic rewrites; only an interrupted write at the wrong instant.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
