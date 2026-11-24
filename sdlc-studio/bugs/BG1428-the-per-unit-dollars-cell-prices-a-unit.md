# BG1428: The per-unit dollars cell prices a unit's Grok agent read from a session total with no lower-bound label, and BG1391's changelog says the label holds wherever models are summed

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_unit_usd_lower_bound.py, changelog.d/BG1391.md, changelog.d/BG1428.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1391, qa-seat-BG1391-r1, verdict sdlc-studio/reviews/verdicts/BG1391/6ef551150470-214c841f.txt ([new] changelog scope and [pre-existing] per-unit gap)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T00:19:15Z

## Summary

`run_state.unit_agent_totals` (lib/`run_state.py`:2630-2638) sums a unit's agent records and `sprint_report._unit_usd` (`sprint_report.py`:4032) prices them with no from-total models passed, so a unit holding a booked Cursor agent and a Grok agent read from a session total reads 'estimated' with no lower-bound reach (probe: $1.73, label 'estimated', the same at base 35d7eaa6 and at c41f87ac). changelog.d/BG1391.md says `run_state.usd` labels those models a lower bound 'wherever they are summed', which the per-unit cell does not yet do.

## Steps to Reproduce

Give one unit a booked Cursor agent record and a Grok agent record read from a session total, close the run and read that unit's dollars cell in the Estimates table: it reads 'estimated' with no lower-bound label.

## Proposed Fix

Carry the from-total model list into the per-unit pricing (`unit_agent_totals` keeps it; `_unit_usd` passes it to `run_state.usd`), so the cell carries the lower-bound label, and the changelog sentence becomes true.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a booked Cursor agent and a Grok agent read from a session total, when the report's Estimates table prints, then that unit's dollars cell carries the lower-bound label. Fails on: the cell reading 'estimated' with no lower-bound reach.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_unit_usd_lower_bound.py::UnitUsdLowerBoundTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A lower-bound label on a per-unit dollar cell.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
