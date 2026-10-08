# CR-0624: Run revert-check at the terminal gate, so a test that passes with the change removed is caught by the tool, not by a reviewer breaking the code by hand

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Evidence:** Operator-relayed assessments of three consuming projects' runs, 2026-10-08. The agent-fleet project: 'Lanes repeatedly wrote tests that passed with the behaviour removed, and the reviewers found them by deliberately breaking the code' (11 of 18 units rejected at least once). verify_ac.py's own revert_check docstring cites RUN-01M0CT8P, where deleting BG0593's whole production change left all four criteria and 916 tests green.
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:37:27Z

## Summary

`verify_ac.py revert-check --unit <id>` already answers the question: it reverts a unit's production files to the base ref and re-runs the unit's own verifiers, and green after the revert is the refusal. Nothing runs it. It is not a lane of `transition -> Done/Fixed`, the close or the review brief, so whether a unit's tests can fail is learned only when an independent reviewer mutates the code by hand, a round later. LL0027: a rule that matters is gated in the command people actually run.

## Impact

Every unit whose tests cannot fail costs a review round to discover it, and a unit whose reviewer does not mutate ships with tests that pin nothing.

## Acceptance Criteria

- [ ] `transition -> Done` (story) and `-> Fixed` (bug) run revert-check over the unit's declared Affects and refuse a unit whose criteria stay green with the production change reverted, naming each criterion, unless `Revert-check-exempt` names it with a reason
- [ ] A unit whose production change cannot be isolated from its tests (no production path in Affects) is reported as not judged, never passed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Raised |
