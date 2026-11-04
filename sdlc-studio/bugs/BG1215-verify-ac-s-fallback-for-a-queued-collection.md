# BG1215: verify_ac's fallback for a queued collection that raised is untested, so dropping it would read a live stamp as stale

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1215.md
> **Evidence:** BG1187 round-1 verdict, scratchpad run5/BG1187-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T17:43:53Z

## Summary

2026-11-04, BG1187's review (qa-seat-BG1187-r1, APPROVE, non-blocking). `_collect_nodes` documents that a queued collection which raised is collected again fresh (`verify_ac.py`:814-815). Mutant M16, returning None after `wait([pending])` (`verify_ac.py`:820) when the cache holds no answer, survives StampsCollectSideBySideTests whole. Exercised alone the branch is right: a server whose `collect` raises still yields `['b.py::t']`. Under the mutant `selector_resolves` reads False and `stamps` would exit 1 on a live stamp.

## Steps to Reproduce

1. Apply M16 at `verify_ac.py`:820.
2. Run `test_verify_ac.py`::StampsCollectSideBySideTests: 5 passed.

## Proposed Fix

Add a fake server whose collect raises, and assert the stamp still resolves with the file collected once fresh.

## Acceptance Criteria

- [ ] **AC1** Mutant M16 fails a test in StampsCollectSideBySideTests.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampsCollectSideBySideTests

## Impact

A later edit can make a failed server collection read every stamp on that file as stale.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
