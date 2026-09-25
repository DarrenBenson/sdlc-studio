# BG0782: About 57 test modules commit in a temporary git repo with auto-maintenance on, the race BG0711 fixed in one

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** conftest.py, tools/skill-tests.sh
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T20:32:48Z

## Summary

BG0711 traced a CI flake to git 2.55's detached 'git maintenance run --auto --detach', which outlives the commit and writes into .git while TemporaryDirectory's cleanup removes it (Errno 39). BG0711 fixed `test_complexity.py` only. 38 modules in scripts/tests and 19 in tools/tests run git commit inside a TemporaryDirectory with default cleanup and auto-maintenance on. Found by BG0711's QA review.

## Steps to Reproduce

grep -l 'git.*commit' scripts/tests tools/tests; each runs on CI's git 2.55 with maintenance.auto unset.

## Proposed Fix

Set maintenance.auto=false suite-wide through `GIT_CONFIG_COUNT`/KEY/VALUE in the root conftest and tools/skill-tests.sh, with one test that a fixture repo reads it false.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0711 traced a CI flake to git 2.55's detached 'git maintenance run --auto --detach', which outlives the commit and writes into .git while...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep -l 'git.*commit' scripts/tests tools/tests; each runs on CI's git 2.55 with maintenance.auto unset.
- [ ] **AC3** The proposed fix lands, pinned by a test: Set maintenance.auto=false suite-wide through `GIT_CONFIG_COUNT`/KEY/VALUE in the root conftest and tools/skill-tests.sh, with one test that a fixture repo...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
