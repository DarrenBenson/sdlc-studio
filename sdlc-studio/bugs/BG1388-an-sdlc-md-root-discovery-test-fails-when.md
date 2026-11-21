# BG1388: An sdlc_md root-discovery test fails when TMPDIR is inside a repository, because it assumes its temporary directory lies outside any project

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_root_discovery_tmpdir_inside_repo.py, changelog.d/BG1388.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane integrity builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:08:17Z

## Summary

The root-discovery test in `test_sdlc_md.py` (around line 1090) passes under /tmp and fails with TMPDIR set to a worktree's .local/tmp, where discovery finds the enclosing repository.

## Steps to Reproduce

TMPDIR=<worktree>/.local/tmp pytest `test_sdlc_md.py.`

## Proposed Fix

Make the test build an isolated root marker.

## Acceptance Criteria

- [ ] **AC1** Given TMPDIR inside a git repository, when the root-discovery tests run, then they pass. Fails on: discovery returning the enclosing repository.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_root_discovery_tmpdir_inside_repo.py::RootDiscoveryTmpdirInsideRepoTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. The test fails only when TMPDIR sits inside a repository, a setup of this repository's own agent worktrees; use another TMPDIR. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
