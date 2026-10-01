# BG0835: Token capture looks for the session transcript in a directory named by replacing only '/', so a project path holding '.' or '_' reads NOT ATTRIBUTABLE

> **Status:** Open
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: a `claude -p` session started in `.../vp2/my_app.v2` wrote its transcript under `~/.claude/projects/-tmp-claude-1000--home-...-vp2-my-app-v2` (every non-alphanumeric to `-`), while `run_state.session_tokens` (line 732) derives `...-vp2-my_app.v2` by replacing `/` only. The literal-form fallback is dropped: the harness never writes it
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir.py, changelog.d/BG0835.md
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

Map every character outside `[A-Za-z0-9]` to `-`, as the harness does (`-` itself stays `-`).

## Acceptance Criteria

- [ ] **AC1** Given a repo root `/x/my_app.v2` holding a session transcript at `$HOME/.claude/projects/-x-my-app-v2/s.jsonl` (HOME pointed at a fixture), when `run_state.session_tokens(root)` runs with no `transcripts_dir` and no env override, then it reads that transcript and returns a token figure, not `no harness transcript directory`. Fails on: HEAD, which looks in `-x-my_app.v2`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir.py::TranscriptDirTests::test_dots_and_underscores_map_to_dashes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
