# BG1387: test_cli_grammar RealTreeMarkerTests copies the whole tree into /tmp and fails with EDQUOT on a small tmpfs

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_real_tree_marker_small_tmpfs.py, changelog.d/BG1387.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane upgrade builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:07:56Z

## Summary

RealTreeMarkerTests (`test_cli_grammar.py`:638) copies the entire repository into /tmp, which fails with EDQUOT where /tmp is a small tmpfs.

## Steps to Reproduce

Run the class with TMPDIR on a 50 MB tmpfs.

## Proposed Fix

Copy only the marker files or use a symlinked tree.

## Acceptance Criteria

- [ ] **AC1** Given a small tmpfs as the temporary directory, when RealTreeMarkerTests runs, then it passes without copying the whole tree. Fails on: EDQUOT.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_real_tree_marker_small_tmpfs.py::RealTreeMarkerSmallTmpfsTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it needs a condition no real install meets. RealTreeMarkerTests copying the repo fails only where /tmp is a small tmpfs, a condition of this repository's test host and not of any install. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
