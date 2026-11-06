# BG1263: The commit-msg hook reads `Refs:` lines below git's scissors line, so a `git commit -v` whose diff shows such a line is refused as a contradicted trailer

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, tools/tests/test_commit_msg_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** run eight (RUN-01M6RZQZ) US1133 review round 1 ([regression] and [new]), and the orchestrator's friction log (R8-F13)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:37:52Z

## Summary

Regression from US1133. `derive_trailers` (`.claude/skills/sdlc-studio/scripts/engagement_floor.py:916`) takes its `Refs:` lines from `_strip_comments(message)`, which drops `#` lines but keeps the verbose diff below the `# ------------------------ >8 ------------------------` line. A diff context line whose text is a space followed by `Refs:` and a unit id is therefore read as the author's trailer, and when that unit owns none of the staged files the commit is refused as contradicted, where the base hook passed it. `with_trailers` itself cuts at `_SCISSORS_RE` (`engagement_floor.py:888`, `:944`) and treats everything below as git's, but that cut has no test either: its mutant survives all four US1133 AC tests. Narrow today: no tracked file at `71120f12` has a line starting `Refs:`.

## Steps to Reproduce

In a fixture repository with two units, commit a file holding the line `Refs: US0002` (US0002 owning no staged file), then change the line beside it and commit with `git commit -v` and a two-id subject carrying the right `Refs:` for the owner: refused, naming US0002 as contradicted. The same commit without `-v` lands.

## Proposed Fix

Cut the message at the scissors line before any trailer is read, in one helper that both `derive_trailers` and `with_trailers` call, and pin it with a hook test that commits with `-v` over such a context line, plus a test that fails when `with_trailers` stops cutting at the scissors.

## Acceptance Criteria

- [ ] **AC1** Following the recorded steps no longer reproduces the defect: In a fixture repository with two units, commit a file holding the line `Refs: US0002` (US0002 owning no staged file), then change the line beside it and commit...
- [ ] **AC2** The proposed fix lands, pinned by a test: Cut the message at the scissors line before any trailer is read, in one helper that both `derive_trailers` and `with_trailers` call, and pin it with a hook...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
