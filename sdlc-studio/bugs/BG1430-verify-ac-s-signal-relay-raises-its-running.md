# BG1430: verify_ac's signal relay raises its running count outside the try, so a raise in that window leaves every later returning handler refused, and no test pins the per-signal refresh of the settle bound

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_relay_bounded_wait.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_relay_count.py, changelog.d/BGXXXX.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1425, qa-seat-BG1425-r1, verdict sdlc-studio/reviews/verdicts/BG1425/786df8f0a468-26807730.txt ([new] test gap, [pre-existing] count leak)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T00:56:42Z

## Summary

A raise between `_RELAYS_RUNNING += 1` and the relay's `try:` (`verify_ac.py`:674-678, since 1caffe6d) leaves the relay count raised for the life of the process, so every later signal whose handler returns no longer carries on: its queued verifiers wait out the four-second bound and are refused (probe at 5a09e949: a second SIGTERM whose handler returns at once gives [false, 'KeyboardInterrupt'] after 4.0 s with the count still 1). Separately, the bound is meant to run from the latest signal (`verify_ac.py`:636-637, set at :673), but the mutant where only the first signal sets `_SETTLE_BY` passes every test: each driver is a fresh process with one signal.

## Steps to Reproduce

In one process, trigger a raise between the relay count's increment and its try (the window case), then send a second SIGTERM whose handler returns at once: the queued verifier is refused after 4 s instead of running. Separately, apply `_SETTLE_BY = _SETTLE_BY or (...)` and run the relay tests: all pass.

## Proposed Fix

Move the increment inside the try (or decrement in a finally that covers it), and add a driver that signals twice, past the first bound, so a deadline set only by the first signal fails.

## Acceptance Criteria

- [ ] **AC1** Given a raise inside the relay window followed by a second signal whose handler returns, when the queued verifiers run, then they run rather than being refused, and the relay count is back to zero. Fails on: the count left raised.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_relay_count.py::RelayCountTests
- [ ] **AC2** Given a caller signalled twice about 5 s apart whose handler returns after 0.5 s, when each signal arrives, then the queued verifier runs on both. Fails on: the deadline set only by the first signal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_relay_count.py::PerSignalBoundTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
