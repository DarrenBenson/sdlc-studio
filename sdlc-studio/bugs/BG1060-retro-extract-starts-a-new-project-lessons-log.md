# BG1060: retro extract starts a new project lessons log when the committed one is missing, though the committed digest lists the lessons that log holds

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_extract_needs_the_log.py, changelog.d/BG1060.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Evidence:** RUN-01M4R168 close on studypc2, 2026-10-16: retros/LESSONS.md absent and LESSONS-SUMMARY.md listing 441 lessons (the log is in studypc's .local/lessons.md); `sprint.py close --dry-run` -> `ok retro-extract`, then `STOP lessons-summary: refused: LESSONS-SUMMARY.md lists 441 lesson(s) the log ... does not hold`. retro.py:3583; lessons.py:871 is the guard extract does not consult. The operator chose to close and carry the gap.
> **Created:** 2026-10-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-16T08:01:04Z

## Summary

BG0989 moved the project lessons log to the committed `sdlc-studio/retros/LESSONS.md` and made `lessons summary` refuse to regenerate a digest from a log that lacks a lesson the committed `LESSONS-SUMMARY.md` lists. `retro.py extract` was given no such guard: with the log absent it starts from `lessons.PROJECT_HEADER` (retro.py:3583) and writes a new log holding only this retro's lessons. On a clone where the log has not yet been migrated (it still sits in another machine's gitignored `.local/lessons.md`), the close's retro-extract step therefore forks the log: the digest is protected, but a short log now exists at the committed path, and the other machine's migration refuses as a two-log conflict that only a person can merge.

## Steps to Reproduce

1. A clone with `sdlc-studio/retros/LESSONS-SUMMARY.md` listing N lessons and no `sdlc-studio/retros/LESSONS.md` or `.local/lessons.md`. 2. `retro.py extract --id RETROxxxx` (or `sprint.py close`, whose retro-extract step runs it). 3. A new LESSONS.md holds only RETROxxxx's lessons; `lessons.py summary` then refuses, naming the N lessons the new log does not hold.

## Proposed Fix

Apply the summary's guard in extract: when the log is absent (or lacks lessons the committed summary lists) and the summary lists lessons, write nothing, name the missing log and the digest's count, and say to restore the log first; the close then carries the step as a known issue rather than forking the log.

## Acceptance Criteria

- [ ] **AC1** With retros/LESSONS.md absent and LESSONS-SUMMARY.md listing lessons, `retro.py extract` writes no log and names the missing log and the digest's count
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_extract_needs_the_log.py -k extract_refuses_to_start_a_log_the_digest_outlives

## Impact

A close on a second machine commits a short lessons log at the committed path, and the full log's migration then needs a hand merge.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-16 | Claude Opus 5.5 | Filed |
