# BG1623: sprint drive and drive step: an oversized brief exits 2 after work ran, a refused paperwork commit re-runs to exit 0, any agent id is accepted as the reviewer, and several guards have no test

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG1623.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** round two of the qa seat on the lane five repair (sdlc-studio/reviews/verdicts/US119[678]/*-r2 files 2ad5df0e4f4b, b01d3c59aca3, bb6e1cb2124b): mutant M16 survives, the run-start filter in _taken (drive.py around 808) has no test that fails without it; R10 kill depends on timing; R7-R9, R12, R14 and R17 still survive
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T17:11:58Z

## Summary

Non-blocking findings from both seats' reviews of the wave driver and its one-step hand-back (run eighteen). Help says exit 2 means nothing ran, but a brief over the size limit exits 2 after build and land ran. Re-running drive after a refused paperwork commit exits 0 with that unit's paperwork uncommitted. drive step's reviewer resolution accepts any agent id, including the unit's own builder, and any unknown id while a round-one verdict waits. Untested: AC1's order check reads drive.STEPS (swapping return and paperwork still passes), the return-step stop, the `_resume_at` worktree check, the `_FINISHING` path, the landing lock, the refusal of a hand-in outside the batch, the shared-file hold, that the paperwork commit runs the hooks, and AC4's flag check covers only drive's own flags. US1198 declares command-audit.md and `test_artifact.py` and changed neither.

## Steps to Reproduce

Run sprint.py drive step --after <the builder's own agent id> on a unit with a written verdict: it records the builder as the reviewer.

## Proposed Fix

Refuse an --after id that is the unit's builder or that no brief names; state exit 2 truthfully or refuse an oversized brief before build; make a re-run after a refused paperwork commit stop; add a failing-first test per guard; drop the unchanged files from US1198's Affects.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from both seats' reviews of the wave driver and its one-step hand-back (run eighteen).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run sprint.py drive step --after <the builder's own agent id> on a unit with a written verdict: it records the builder as the reviewer.
- [ ] **AC3** The proposed fix lands, pinned by a test: Refuse an --after id that is the unit's builder or that no brief names; state exit 2 truthfully or refuse an oversized brief before build; make a re-run after...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
