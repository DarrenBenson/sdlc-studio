# BG1209: The pre-commit hook's payload markdown lane quotes its markdownlint path untested, because the BG1147 fixture tracks no markdown under .claude/

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_commit_lanes.py, changelog.d/BG1209.md
> **Evidence:** BG1147 round-1 verdict, scratchpad run5/BG1147-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T15:50:10Z

## Summary

2026-11-04, BG1147's review (qa-seat-BG1147-r1, APPROVE, non-blocking). BG1147 quoted `"$md_cmd"` in both markdown lanes. The payload lane (.githooks/pre-commit:355) has no test: the fixture tracks no markdown under `.claude/`, so that lane always skips, and an unquoted `$md_cmd` there passes. Run alone, that mutation breaks a payload-markdown commit when the main tree's path holds a space.

## Steps to Reproduce

1. Unquote `$md_cmd` on the payload lane.
2. Run the BG1147 tests in tools/tests/`test_lean_commit_lanes.py`: they pass.

## Proposed Fix

Add a tracked markdown file under `.claude/` to the fixture so the payload lane runs in the spaced-path test.

## Acceptance Criteria

- [ ] **AC1** Unquoting `$md_cmd` on the payload lane fails a test.
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::LaneCapTests

## Impact

A later edit can break payload markdown commits for a clone under a path with a space, with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
