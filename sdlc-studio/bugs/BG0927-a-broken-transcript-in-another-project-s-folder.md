# BG0927: A broken transcript in another project's folder crashes the long-path transcript scan

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_scan_dangling.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG0927.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T03:28:19Z

## Summary

BG0882 finds a long-path project's transcript folder by scanning every folder under projects/ for the cwd its newest transcript records; a dangling transcript link in an unrelated folder raises FileNotFoundError, which `sprint_report.py` (~4147) does not catch, so building the report fails.

## Steps to Reproduce

1. A project path over 200 characters. 2. A dangling .jsonl symlink in another projects/ folder. 3. Build the report: FileNotFoundError.

## Proposed Fix

Skip a transcript that cannot be read while scanning, as an unreadable one elsewhere is skipped. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a long-path project and a dangling transcript in an unrelated projects/ folder, when the transcript folder is resolved, then the right folder is returned and nothing raises. Fails on: the current scan, which raises FileNotFoundError
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_scan_dangling.py::TranscriptScanDanglingTests::test_a_dangling_transcript_is_skipped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
