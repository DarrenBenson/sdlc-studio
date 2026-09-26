# BG0791: test_lean_cr_filing reads a changelog fragment that the release cut consumes, so the suite goes red on every release commit

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T16:25:39Z

## Summary

tests/`test_lean_cr_filing.py` scans changelog.d/US0900.md by path; changelog-cut folds every fragment into CHANGELOG.md and deletes them, so the release-prep commit for v6.0.0-rc.1 turned the skill suite red (1 error in 6,794). Fixed in the rc.1 release commit by dropping the consumed path from the scan.

## Steps to Reproduce

Run `release_cut.py` changelog-cut, then pytest tests/`test_lean_cr_filing.py`: FileNotFoundError on changelog.d/US0900.md.

## Proposed Fix

Scan only files that exist after a cut, with no path to a fragment the cut consumes.

## Acceptance Criteria

- [ ] **AC1** Given the tree after `release_cut.py changelog-cut` has consumed every fragment, when `test_lean_cr_filing` runs, then it passes and names no path under `changelog.d/`. Fails on: a scan list naming a fragment the cut deletes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
