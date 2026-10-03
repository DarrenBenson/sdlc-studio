# BG0932: A broken or self-looping transcript link still crashes the report

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_links_skipped.py, changelog.d/BG0932.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:08:02Z

## Summary

BG0927 skips a transcript whose stat raises FileNotFoundError while the folder is chosen, but a dangling link in the matching project folder still crashes the report through `session_tokens` (`run_state.py` ~797), and a self-looping link raises ELOOP (an OSError BG0927 does not catch). Found by the v6.1 BG0927 review (D0326).

## Steps to Reproduce

1. A dangling .jsonl link in the project's own transcript folder: build the report, it raises. 2. A self-looping .jsonl link: the folder scan raises ELOOP.

## Proposed Fix

Skip any transcript whose stat or read raises OSError, in the folder scan and in `session_tokens.` No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given the project's own transcript folder holding a dangling link and a self-looping link beside a real transcript, when the report's token reading runs, then it reads the real transcript and nothing raises. Fails on: the current code, which raises
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_links_skipped.py::TranscriptLinksSkippedTests::test_broken_and_looping_links_are_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
