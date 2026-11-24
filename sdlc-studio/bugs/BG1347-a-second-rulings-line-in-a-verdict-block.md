# BG1347: A second RULINGS: line in a verdict block is silently dropped

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_verdict_rulings_lines.py, changelog.d/BG1347.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-BG1030-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:35Z

## Summary

critic.py keeps only the first RULINGS line of a verdict block (critic.py:3632); a second is lost without a warning. Reported non-blocking at review.

## Steps to Reproduce

Apply the surviving mutant the review names: the suite stays green.

## Proposed Fix

Add the pin.

## Acceptance Criteria

- [ ] **AC1** Given the behaviour named, a test fails when it is broken. Fails on: the surviving mutant the review named.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verdict_rulings_lines.py::RulingsLinesTests::test_a_second_rulings_line_is_kept_or_refused

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because a user can meet it, but it is rare and harmless and has a workaround, so fixing it costs more than it returns. A second RULINGS line is dropped; workaround is one line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
