# BG1253: lib/lanes.py clears only 7 of the 11 repo-locating git variables before it runs a lane

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, tools/tests/test_skill_tests_env.py, changelog.d/BG1253.md
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

- [ ] **AC1** Given an environment with every variable of `REPO_LOCATING` set, when `lib/lanes.py` builds a lane's child environment, then none of them remains, and the module's `SCRUB_SITES` entry no longer begins PARTIAL. Fails on: `GIT_INDEX_VERSION`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` or `GIT_DISCOVERY_ACROSS_FILESYSTEM` reaching the lane.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::ScrubListsAgreeTests::test_the_lane_runner_scrub_clears_every_repo_locating_variable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
