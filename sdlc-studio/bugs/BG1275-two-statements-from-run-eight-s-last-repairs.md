# BG1275: Two statements from run eight's last repairs claim more than the code or its tests show

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1274 round-2 and BG1273 round-1 QA verdicts, non-blocking findings
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T21:39:18Z

## Summary

BG1274's round-2 review: the `_declared_tokens` docstring says a bracketed note holding a comma yields fragments `_is_file_token` then drops, but a note listing two or more paths keeps a fragment that is counted. BG1273's review: the `engagement_floor.py` allowlist reason in `test_confinement.py` says the hook tests pin that it writes only the message file, but no test asserts that no other file is written.

## Steps to Reproduce

Read `engagement_floor.py` near line 445 and the `engagement_floor.py` entry in `CONFINEMENT_ALLOWLIST`, then run each against a fixture: a note listing two paths, and a `--write-trailers` run that checks every file it touched.

## Proposed Fix

Narrow the docstring to the shapes it holds for, and either add a test that `--write-trailers` writes only the message file or drop that clause from the allowlist reason.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1274's round-2 review: the `_declared_tokens` docstring says a bracketed note holding a comma yields fragments `_is_file_token` then drops, but a note...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read `engagement_floor.py` near line 445 and the `engagement_floor.py` entry in `CONFINEMENT_ALLOWLIST`, then run each against a fixture: a note listing two...
- [ ] **AC3** The proposed fix lands, pinned by a test: Narrow the docstring to the shapes it holds for, and either add a test that `--write-trailers` writes only the message file or drop that clause from the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
