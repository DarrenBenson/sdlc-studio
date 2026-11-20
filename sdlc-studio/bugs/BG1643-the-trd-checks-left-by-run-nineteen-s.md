# BG1643: The TRD checks left by run nineteen's TRD repairs accept rewordings and leave three claims unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:41:24Z

## Summary

The builder of the BG1516, BG1517 and BG1531 repairs (RUN-01M7TTK3) left these non-blocking gaps. BG1516: AC1's 'which worktree' is pinned by no test, an AC3 mutant that changes only words survives, and the TRD does not name Codex's --skip-git-repo-check among the flags the lane runner passes. BG1517: the exfiltration row's opening clause in sdlc-studio/trd.md reads as if Verify-line commands cannot reach the network, which its later clauses contradict, and `verify_ac`'s `shell_allowed_for` with `allow_external` is pinned by no test. BG1531: other phrasings of the read-only helper list escape the check.

## Steps to Reproduce

In a throwaway copy, reword the read-only helper list in sdlc-studio/trd.md (for example 'these helpers only read') to list critic brief again, and run tools/tests/`test_lean_trd_refresh.py`: green.

## Proposed Fix

Pin the worktree path the TRD names, judge the read-only list by meaning rather than one phrasing, name --skip-git-repo-check, reword the exfiltration row's opening clause, and add a `shell_allowed_for` test with `allow_external` on.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The builder of the BG1516, BG1517 and BG1531 repairs (RUN-01M7TTK3) left these non-blocking gaps.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a throwaway copy, reword the read-only helper list in sdlc-studio/trd.md (for example 'these helpers only read') to list critic brief again, and run...
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin the worktree path the TRD names, judge the read-only list by meaning rather than one phrasing, name --skip-git-repo-check, reword the exfiltration row's...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
