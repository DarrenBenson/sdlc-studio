# BG1378: US1134's AC3 skips markdownlint without saying so when the binary is missing

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py, changelog.d/BG1378.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1134-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T16:24:47Z

## Summary

With no markdownlint installed, AC3's test passes silently instead of naming the skip. Reported non-blocking at review.

## Steps to Reproduce

Apply the mutant the review names; the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the case the review named, a test fails when it is broken. Fails on: the surviving mutant.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_quiet_success.py::QuietSuccessTests::test_a_missing_markdownlint_is_named

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. One repository test passes silently without markdownlint; the lint still runs in CI where the binary exists. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
