# CR-0607: A carry bug filed at the review cap does not count against the triage session cap

> **Status:** In Progress
> **Decomposed-into:** EP0271
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_uncapped.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Date:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T09:29:50Z

## Summary

D0297: when critic.py record carries a unit at the review cap it files a carry bug through the same triage counter as a new finding, so six carries in RUN-01M3VF2J consumed six of the run's finding allowance and real findings were deferred until after the seal. A carry bug records a review outcome, not a new finding.

## Impact

A run with several carries reaches the triage cap early and defers genuine findings.

## Acceptance Criteria

- [ ] Given a triage session cap of 2 and two findings already filed in the session, when critic.py record carries a unit at the review cap, then its carry bug is filed and the session's finding count stays at 2, so a third ordinary finding is still refused. Fails on: the current code refuses the carry bug at the cap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_carry_bug_uncapped.py::CarryBugUncappedTests::test_a_carry_bug_is_filed_past_the_cap_and_not_counted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Raised |
