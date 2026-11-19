# BG1451: The commit-msg hook refuses git commit --amend on a lane commit because it attributes only the newly staged files

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/commit-msg, tools/tests/test_commit_msg_amend.py, changelog.d/BG1451.md, .claude/skills/sdlc-studio/scripts/engagement_floor.py
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:38:10Z

## Summary

Amending US1150/US1151's lane commit to add two files US1151 owns was refused: the hook attributed only the staged files and rejected the commit's existing `Refs: US1150` trailer. The builder had to soft-reset and recommit the whole lane.

## Steps to Reproduce

Amend a two-unit commit with a file only one unit owns: the other unit's Refs trailer is refused.

## Proposed Fix

On an amend, attribute the whole resulting commit's files (HEAD's plus the staged), not only the staged ones.

## Acceptance Criteria

- [ ] **AC1** Given an amend of a two-unit lane commit adding one unit's file, when the hook runs, then both Refs trailers are accepted. Fails on: the other unit's trailer refused.
  - **Verify:** pytest tools/tests/test_commit_msg_amend.py::CommitMsgAmendTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
