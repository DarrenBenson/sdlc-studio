# BG0309: TRD and TSD both claim the suite runs 'in under a minute' - falsified by the repo's own measured ~198s over 4,537 tests

> **Status:** Fixed
> **Verification depth:** functional (executable checks against the specs)
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/trd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Both specs anchor scaling and gate-design claims on a suite that runs '2,500+ tests in under a minute'; the repo's committed measurements say ~198s and 4,537 tests, and AGENTS.md documents the hook skipping the suites precisely because they are too slow to pay on every commit - the performance characterisation of the primary gate is stale by ~3x on time and ~1.8x on count.

## Steps to Reproduce

Evidence (trd.md lines 563 and 610; tsd.md lines 188, 191-192, 367): .config.yaml `gate_budget` comment (2026-07-26): 'measured ~317s peak (skill-tests ~198s ...)'; AGENTS.md: 'unit suites are the one slow guard (~2.5 min)' and the docs-only skip; RV0020: 'full suite 4537'; trd.md:563/:610 and tsd.md:188/:191-192 all say under a minute.

## Proposed Fix

Update both documents to the measured figures (~4,500 tests, ~2.5-3 min) and restate the pre-commit rationale as it actually works: the hook pays the cost only on test-relevant commits and skips otherwise.

## Acceptance Criteria

### AC1: no spec claims the suite runs in under a minute

- **Given** the TRD and TSD performance claims
- **When** the specs are read
- **Then** neither says 'under a minute' - the recorded runs are 215-265s and 80-90s, and the hook skips the suites precisely because they are too slow to pay on every commit
- **Verify:** shell ! grep -q 'under a minute' sdlc-studio/trd.md sdlc-studio/tsd.md
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
