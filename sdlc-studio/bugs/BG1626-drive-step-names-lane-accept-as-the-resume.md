# BG1626: drive step names lane accept as the resume of a warning stop at accept, which lane accept refuses because the verdict is already recorded

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, changelog.d/BG1626.md, .claude/skills/sdlc-studio/scripts/tests/test_drive_step_accept_resume.py, .claude/skills/sdlc-studio/help/sprint.md
> **Evidence:** round two of the qa seat on US1198 (sdlc-studio/reviews/verdicts/US1198/bb6e1cb2124b-18b672fa.txt): drive step can report a wave ended while a unit's paperwork is uncommitted, because `_next_prompt` reads status from the working tree (drive.py around 824), so the repair's HEAD check for the walk does not reach step mode
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T17:44:27Z

## Summary

The repair of US1197 made a warning stop at accept resumable under sprint.py drive, but sprint.py drive step's own stop at the same point still prints a resume naming 'sprint.py lane accept', which exits 2 because a verdict file is recorded once. The step-mode hand-back is left with a resume that does not resume. Found by the repair builder of run eighteen's lane five.

## Steps to Reproduce

Drive a unit through drive step to an APPROVE whose accept stops on a warning, then run the resume the step prints: lane accept exits 2 with 'a verdict file is recorded once'.

## Proposed Fix

Have drive step name the command that resumes from the recorded accept (the same path drive now takes), and pin it with a test that runs the printed resume.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose APPROVE accept stopped on a warning under `sprint.py drive step`, when the resume command the step prints is run, then it succeeds and resumes from the recorded accept, as `sprint.py drive` does. Fails on: the printed `lane accept` exiting 2 with 'a verdict file is recorded once'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_drive_step_accept_resume.py::DriveStepAcceptResumeTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-22 | Claude Sonnet 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-two) |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Affects widened to `help/sprint.md`, whose resume paragraph the fix's behaviour changes (qa round one) |
