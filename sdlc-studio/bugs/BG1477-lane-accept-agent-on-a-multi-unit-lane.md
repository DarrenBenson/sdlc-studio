# BG1477: lane accept --agent on a multi-unit lane charges the builder's whole transcript to each unit, overriding the land's split by points

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1477.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** sdlc-studio/reports/RPT0032-sprint-report-run-01m7eyr3.md, unit cost rows for US1066 and BG1459.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T20:40:35Z

## Summary

`sprint.py lane land` prices a multi-unit lane's return from the builder's transcript split by points (US1065 3 of 9, US1066 5 of 9, BG1459 1 of 9 in run thirteen). When `lane accept --unit <id> --agent <builder>` then calls `lane return` with that agent, the unit is re-priced with the builder's whole total: RPT0032 shows US1066 and BG1459 each at 659,978 agent tokens and $10.44, though BG1459 is one point. Per-unit cost rows are inflated, while the run's headline cost, read from the meter, is right.

## Steps to Reproduce

1. Land a two-unit lane with `lane land`.
2. Accept each unit with `lane accept --unit <id> --verdict <file> --reviewer <name> --agent <builder id>`.
3. Read the report's per-unit cost table: each unit carries the whole builder total.

## Proposed Fix

When the unit's return was already priced by the land from the same agent, have accept keep that split (or refuse --agent with a note); otherwise split a multi-unit agent's total by points as the land does.

## Acceptance Criteria

- [ ] **AC1** Given a two-unit lane landed with `sprint.py lane land`, which priced each unit's return from the builder's transcript split by points, when each unit is accepted with `lane accept --agent <builder id>`, then each unit's recorded return keeps its share and the shares sum to the builder's total. Fails on: each unit re-priced with the builder's whole total.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandPricesTheBuilderTests::test_an_accept_naming_the_builder_keeps_the_lands_split
- [ ] **AC2** Given a unit the land did not price, when it is accepted with `lane accept --agent <id>`, then its return is priced from that agent's transcript as before. Fails on: the fix dropping the price of a unit only the accept prices.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandPricesTheBuilderTests::test_an_accept_still_prices_a_unit_the_land_did_not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
