# BG1343: Moving a story to Ready does not refuse a criterion with several stacked Verify lines, which then turns main red at StackedVerifierTests

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, changelog.d/BG1343.md, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Evidence:** RUN-01M77177, 2026-11-12: US1134 AC4 at 227ba263, fixed at 11c5ba15
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:11Z

## Summary

`test_verify_ac`'s StackedVerifierTests refuses, across the workspace, a criterion carrying more than one Verify line. Grooming and `transition.py set --status Ready` accept one, so the first commit after the groom fails that test on main.

## Steps to Reproduce

Give one criterion two Verify lines and move the story to Ready: it moves; then run StackedVerifierTests: red.

## Proposed Fix

Apply the stacked-verifier rule in the Ready gate (readiness.py) so it refuses where the workspace test would.

## Acceptance Criteria

- [ ] **AC1** Given a story whose criterion has two Verify lines, when it is moved to Ready, then the move is refused naming the criterion. Fails on: Ready reached with stacked verifiers.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ReadyGateTests::test_stacked_verifiers_refuse_ready
  - **Verified:** yes (2026-11-12)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
