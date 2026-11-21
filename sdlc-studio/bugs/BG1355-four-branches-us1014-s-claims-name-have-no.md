# BG1355: Four branches US1014's claims name have no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py, changelog.d/BG1355.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1014-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:23Z

## Summary

US1014's self-check claims four branches of verdict provenance that no test drives. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_provenance.py::VerdictProvenanceTests::test_the_claimed_branches_are_pinned

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. US1014's four provenance branches behave correctly; no test drives them. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
