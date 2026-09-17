# US0827: a module the selection omitted and the sweep later finds red is recorded as a miss, so the rule is judged on evidence

> **Status:** Draft
> **Delivers:** CR0586
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0253
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a module the selection omitted and the sweep later finds red is recorded as a miss, so the rule is judged on evidence
**So that** CR0586 is delivered by work that can be planned and checked

## Acceptance Criteria

An advisory ledger with no threshold is a third instrument that accumulates and decides nothing - `revert-check` and `claim-drift` already do that here, and both personas named the pattern.

### AC1: a module the selection skipped and the sweep found red is recorded as a miss, with what would have selected it

- **Given** a weekly sweep finding `test_x` red, and the pushes since the last green sweep
- **When** the miss is recorded
- **Then** the ledger row carries the module, the push that introduced the failure, and the import edge the selection would have needed to catch it
- **Mutant:** record the module and date alone - the rule cannot then be improved from its own misses, only counted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneMissTests::test_a_miss_records_the_edge_that_would_have_caught_it

### AC2: the miss rate carries a stated threshold and the lane says which side it is on

- **Given** a miss ledger over a declared window
- **When** the lane reports
- **Then** it states the miss rate against a threshold recorded in config, and names the consequence of crossing it - the selection reverts to the full sweep at the push boundary until a delivery lowers it
- **Mutant:** report the rate with no threshold - the ledger then joins the two advisory instruments this repository already cannot act on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneMissTests::test_the_miss_rate_is_judged_against_a_recorded_threshold

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
