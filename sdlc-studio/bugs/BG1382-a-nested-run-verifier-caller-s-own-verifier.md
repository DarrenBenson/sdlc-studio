# BG1382: A nested run_verifier caller's own verifier can outlive it, because both levels wait the same one second grace and Ctrl-C leaks the inner verifier

> **Status:** Won't Fix
> **Supersedes:** BG1418
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py, changelog.d/BG1382.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane reaper builder and review reaper, BG1190 and BG1228
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:05:14Z

## Summary

When a verifier is itself a `run_verifier` caller and ignores SIGTERM, the outer and inner kills each wait the same 1 s grace, so the inner group was still alive in 1 of 3 probes. A Ctrl-C to such a nested caller leaks the inner verifier in 2 of 3 rounds, as it did before the reaper fix (AC5 part still open). `_kill_group` and `_reap_on_signal` in `verify_ac.py` are the sites.

## Steps to Reproduce

Run a verify line whose command runs `verify_ac` on a verifier that traps SIGTERM, then time it out or send SIGINT; probe the inner group three times.

## Proposed Fix

Give the outer level a grace longer than the inner one, and have the signal handler wait for the group before re-raising.

## Acceptance Criteria

- [ ] **AC1** Given a verifier that runs a nested `run_verifier` caller whose own verifier ignores SIGTERM, when the outer verifier times out or receives SIGINT, then no process of the inner group is alive once the outer call returns. Fails on: the inner group alive after the outer returns.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py::NestedVerifierReapTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it needs a condition no real install meets. Needs a verifier that is itself a run_verifier caller and ignores SIGTERM; no shipped verifier does, and the leak is a stray process. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
