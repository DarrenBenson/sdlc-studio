# BG1500: help/retro.md says an escaped defect is charged to the seat whose latest verdict approved, in any run, leaving out the code's limit to verdicts on or before the bug's Created day

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/retro.md, changelog.d/BG1500.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1171 QA verdict 204ec71c3de6-bdf90726, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T06:11:51Z

## Summary

Run fifteen's US1171 QA seat found that help/retro.md (near line 68) says an escaped defect's charge goes to every seat whose latest verdict on the unit approved, in any run, while the code counts only verdicts recorded on or before the bug's Created day. A reader would expect a later approval to be charged with an earlier escape, which the code never does.

## Steps to Reproduce

Read help/retro.md near line 68 against the seat-evidence charge in retro.py.

## Proposed Fix

Add the on-or-before-Created limit to the help sentence, matching reference-retro.md's seat-evidence section and the code.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run fifteen's US1171 QA seat found that help/retro.md (near line 68) says an escaped defect's charge goes to every seat whose latest verdict on the unit...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read help/retro.md near line 68 against the seat-evidence charge in retro.py.
- [ ] **AC3** The proposed fix lands, pinned by a test: Add the on-or-before-Created limit to the help sentence, matching reference-retro.md's seat-evidence section and the code.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
