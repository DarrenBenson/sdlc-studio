# BG1260: `init run` and `init guided` exit 1 and leave a half-built project when `.claude` is a regular file, which the base initialised cleanly

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_stage_confirm.py
> **Evidence:** run eight (RUN-01M6RZQZ) US1131 review round 1 ([regression] and [new]), and the orchestrator's friction log (R8-F2)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:33Z

## Summary

Regression from US1131. Drafting the shipped agent definitions (`AGENT_DEFINITIONS`, `.claude/skills/sdlc-studio/scripts/init.py:75-77`) creates `.claude/agents/`, and where `.claude` is a regular file the `NotADirectoryError` is not caught per file (`init.py:531` in `init run`, `init.py:769` through `_write` in `init guided`, lines at review round 1), so both exit 1 with the tree half written. At `fd1c2b5b` the same project initialised cleanly. The input is rare, the error is reported cleanly and a re-run after moving the file recovers, so the reviewer did not hold the gate. A second gap from the same review: narrowing the unreadable-file check to `INSTRUCTION_FILES` (`init.py:537`) has no test. Widening it back to `AGENT_FILES` passes `test_init.py` and `test_lean_guided_stage_confirm.py`, and then an unreadable definition prints a false 'so the doctrine check can read it' directive and, through the `if not unreadable` guard (`init.py:542`), hides the doctrine offer.

## Steps to Reproduce

In a fixture directory create `.claude` as an empty regular file, then run `init run` and `init guided` against it: each exits 1 reporting `NotADirectoryError`, with the instruction files partly written. At `fd1c2b5b` the same fixture exits 0. For the second gap, make the unreadable-file check at `init.py:537` iterate `AGENT_FILES` and run `test_init.py` and `test_lean_guided_stage_confirm.py`: both stay green.

## Proposed Fix

Catch `OSError` per definition file while drafting `.claude/agents/`, report the definition skipped with its reason, and let the stage finish the instruction files and exit 0 as the base did. Add a test with `.claude` as a regular file for `init run` and `init guided`, and one that an unreadable agent definition neither prints the doctrine-check directive nor hides the doctrine offer.

## Acceptance Criteria

- [ ] **AC1** Following the recorded steps no longer reproduces the defect: In a fixture directory create `.claude` as an empty regular file, then run `init run` and `init guided` against it: each exits 1 reporting...
- [ ] **AC2** The proposed fix lands, pinned by a test: Catch `OSError` per definition file while drafting `.claude/agents/`, report the definition skipped with its reason, and let the stage finish the instruction...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
