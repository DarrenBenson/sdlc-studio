# BG1446: Three second-seat behaviours are correct but unpinned: a story's risk tag read over its Affects, the brief's no-map default, and the first seat's latest verdict rather than its first

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_second_seat_pins.py, changelog.d/BG1446.md
> **Evidence:** Run twelve (RUN-01M7E52T) US1154 round-2 review, qa-seat-US1154-r1, verdict sdlc-studio/reviews/verdicts/US1154/7642fe83428a-dec20b04.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:27:50Z

## Summary

Run twelve's US1154 round-2 review (APPROVE, non-blocking): `unit_risk_class` reads a story's tag over its Affects (critic.py:3348) but every fixture's tag agrees with its Affects; its no-map default (critic.py:3345) has no brief test without a map; and the retro's yield uses the first seat's latest verdict rather than its first (retro.py:1372) with no fixture where the first seat goes REJECT then APPROVE before the second seat raises an issue. Each mutant survives `test_second_seat.py`; the code is right by execution.

## Steps to Reproduce

Apply each of the three mutants named in the summary and run `test_second_seat.py`: each survives.

## Proposed Fix

Add fixtures: a story whose tag disagrees with its Affects, a brief with no map, and a first seat that rejects then approves before the second seat raises an issue.

## Acceptance Criteria

- [ ] **AC1** Given each of the three mutants, when the second-seat tests run, then each fails. Fails on: any surviving.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_second_seat_pins.py::SecondSeatPinTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Code is right by execution; the second-seat behaviours only lack fixtures. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
