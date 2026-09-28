# BG0835: Token capture looks for the session transcript in a directory named by replacing only '/', so a project path holding '.' or '_' reads NOT ATTRIBUTABLE

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir.py, changelog.d/BG0835.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** US0965 rehearsal friction note; HEAD 7e53a438 lib/run_state.py:677 replaces '/' only (the harness mapping of '.' and '_' was not re-executed here)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:41Z

## Summary

`run_state` derives the harness transcript directory as `~/.claude/projects/` + the resolved root with `/` replaced by `-` (`run_state.py`:677). The US0965 rehearsal found the harness also maps `.` and `_` to `-`, so on a fixture path holding either the directory is not found and the report's token actual reads NOT ATTRIBUTABLE. Project paths such as `my_app` or `site.example` meet it.

## Steps to Reproduce

Open and close a run in a repo at a path containing `_`: the report's token actual reads NOT ATTRIBUTABLE with `no harness transcript directory at ...`.

## Proposed Fix

Map every character outside [A-Za-z0-9-] to `-`, as the harness does, and fall back to the literal form when that directory is absent.

## Acceptance Criteria

- [ ] **AC1** Given a repo root `/x/my_app.v2`, then the derived transcript directory is `-x-my-app-v2`. Fails on: HEAD's `-x-my_app.v2`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir.py::TranscriptDirTests::test_dots_and_underscores_map_to_dashes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
