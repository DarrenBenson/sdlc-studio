# BG1377: The hooks' replay of a refusal's stderr is not pinned

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, tools/tests/test_quiet_hooks.py, changelog.d/BG1377.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1134-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:24:42Z

## Summary

Mutants at .githooks/pre-commit:189 and .githooks/commit-msg:105 that drop the stderr replay on a refusal survive US1134's tests. Reported non-blocking at review.

## Steps to Reproduce

Apply the mutant the review names; the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, a test fails when it is broken. Fails on: the surviving mutant.
  - **Verify:** pytest tools/tests/test_quiet_hooks.py::QuietHooksTests::test_a_refusal_replays_its_stderr

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
