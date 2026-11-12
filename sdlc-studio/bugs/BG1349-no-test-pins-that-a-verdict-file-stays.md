# BG1349: No test pins that a verdict file stays under --root inside a larger git repository

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py, changelog.d/BG1349.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1011-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:49Z

## Summary

critic.py:204 keeps the verdict path under --root when that folder sits inside a bigger repository; the behaviour is right but unpinned. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_a_root_inside_a_larger_repo_keeps_its_verdicts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
