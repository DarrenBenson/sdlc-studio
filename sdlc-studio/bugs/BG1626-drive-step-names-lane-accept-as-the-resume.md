# BG1626: drive step names lane accept as the resume of a warning stop at accept, which lane accept refuses because the verdict is already recorded

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/drive.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive_step.py, changelog.d/BG1626.md
> **Evidence:** run eighteen, 2026-11-19: hand-back of the lane five repair builder
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

- [ ] **AC1** The behaviour described is corrected: The repair of US1197 made a warning stop at accept resumable under sprint.py drive, but sprint.py drive step's own stop at the same point still prints a resume...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Drive a unit through drive step to an APPROVE whose accept stops on a warning, then run the resume the step prints: lane accept exits 2 with 'a verdict file is...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have drive step name the command that resumes from the recorded accept (the same path drive now takes), and pin it with a test that runs the printed resume.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
