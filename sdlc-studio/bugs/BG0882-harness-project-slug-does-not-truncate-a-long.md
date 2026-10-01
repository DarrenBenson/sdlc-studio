# BG0882: harness_project_slug does not truncate a long project path or map non-BMP characters as the harness does

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** BG0835 QA review (RUN-01M3VF2J), rule read from the installed Claude Code 2.1.284 binary
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T17:43:53Z

## Summary

Claude Code 2.1.284 names a project's transcript folder by mapping each UTF-16 code unit outside [A-Za-z0-9] to '-', and truncates a slug longer than 200 characters to 200 plus '-' and a base36 hash. `run_state.harness_project_slug` maps per code point and never truncates, so a repo under a deep path, or with an emoji in its path, reads its token meter as NOT ATTRIBUTABLE.

## Steps to Reproduce

1. A repo at a path whose slug exceeds 200 characters. 2. `run_state.session_tokens` -> no transcript found (337-char slug vs the harness's 207).

## Proposed Fix

Mirror the harness rule: map per UTF-16 code unit and truncate past 200 with the harness's hash suffix, or locate the folder by matching the recorded cwd inside each transcript.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Claude Code 2.1.284 names a project's transcript folder by mapping each UTF-16 code unit outside [A-Za-z0-9] to '-', and truncates a slug longer than 200...
- [ ] **AC2** The proposed fix lands, pinned by a test: Mirror the harness rule: map per UTF-16 code unit and truncate past 200 with the harness's hash suffix, or locate the folder by matching the recorded cwd...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
