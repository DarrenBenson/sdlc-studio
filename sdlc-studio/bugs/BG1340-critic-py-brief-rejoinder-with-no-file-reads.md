# BG1340: critic.py brief --rejoinder with no file reads only the unit's current delivery, so a unit carried across runs has no ledger rejoinder

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, changelog.d/BG1340.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M77177, 2026-11-12: US1147
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:53Z

## Summary

A unit carried at the review cap reaches Done in a later run on an APPROVE from the seat that rejected it (D0433). Its REJECT is in an earlier delivery, so the ledger rejoinder refuses ('no unanswered REJECT from a qa reviewer in its current delivery'), while `sprint plan`'s close-requirement check reports the same REJECT as unanswered. The orchestrator has to find a saved verdict file.

## Steps to Reproduce

Brief US1147's qa seat with a bare --rejoinder in run ten: refused.

## Proposed Fix

Treat an unanswered REJECT of a carried unit as current, the way sprint plan's check does.

## Acceptance Criteria

- [ ] **AC1** Given a carried unit whose seat's REJECT is in an earlier delivery and unanswered, when `critic.py brief --unit <id> --seat <seat> --rejoinder` runs, then it quotes that REJECT. Fails on: the refusal naming no unanswered REJECT while sprint plan reports one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py::RejoinderFromLedgerTests::test_a_carried_units_earlier_reject_is_quoted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
