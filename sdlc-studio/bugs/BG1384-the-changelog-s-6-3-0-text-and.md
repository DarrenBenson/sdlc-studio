# BG1384: The changelog's 6.3.0 text and the BG1112 fragment still over-state what the group kill does

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** CHANGELOG.md, .claude/skills/sdlc-studio/scripts/tests/test_changelog_wording.py, changelog.d/BG1384.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane reaper builder; BG1112 review
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:06:55Z

## Summary

CHANGELOG.md lines 838-845 carry 6.3.0's over-stated wording that a SIGKILL means children no longer run, which only the new fragment corrects. The BG1112 fragment's headline also over-states the fix.

## Steps to Reproduce

Read CHANGELOG.md lines 838-845 and changelog.d/BG1112.md.

## Proposed Fix

Correct the 6.3.0 entry in place and narrow the BG1112 headline.

## Acceptance Criteria

- [ ] **AC1** Given CHANGELOG.md and the unreleased fragments, when the group-kill entries are read, then none says children can no longer run after a SIGKILL or claims more than the fix does. Fails on: the 6.3.0 lines 838-845 wording standing uncorrected.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_changelog_wording.py::ChangelogGroupKillWordingTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
