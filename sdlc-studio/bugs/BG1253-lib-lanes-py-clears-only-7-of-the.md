# BG1253: lib/lanes.py clears only 7 of the 11 repo-locating git variables before it runs a lane

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, tools/tests/test_skill_tests_env.py
> **Evidence:** run seven (RUN-01M6RAP7) BG1238 build
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:58:35Z

## Summary

`_GIT_ENV` in `lib/lanes.py` (from US1126) does not clear `GIT_INDEX_VERSION`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` or `GIT_DISCOVERY_ACROSS_FILESYSTEM`, so a lane started from a hook or a nested git process can inherit them; the BG1238 builder registered the site as PARTIAL with a floor test.

## Steps to Reproduce

Compare `lib/lanes.py` `_GIT_ENV` with `REPO_LOCATING` in `tools/tests/test_skill_tests_env.py`.

## Proposed Fix

Clear the full repo-locating set in `lib/lanes.py`, or derive it from the shared list, and move its `SCRUB_SITES` entry from PARTIAL to full.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `_GIT_ENV` in `lib/lanes.py` (from US1126) does not clear `GIT_INDEX_VERSION`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` or `GIT_DISCOVERY_ACROSS_FILESYSTEM`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Compare `lib/lanes.py` `_GIT_ENV` with `REPO_LOCATING` in `tools/tests/test_skill_tests_env.py`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Clear the full repo-locating set in `lib/lanes.py`, or derive it from the shared list, and move its `SCRUB_SITES` entry from PARTIAL to full.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
