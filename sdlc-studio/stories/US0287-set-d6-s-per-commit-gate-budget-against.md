# US0287: Set D6's per-commit gate budget against the improved baseline and pin the ratchet

> **Status:** Draft
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml,tools/gate_timing.py,.githooks/pre-commit,tools/tests/test_gate_timing.py,sdlc-studio/rfcs/RFC0048-make-the-test-suite-cost-effective-without-lowering.md
> **Epic:** EP0093
> **Points:** 2
> **Depends on:** US0284, US0285, US0286
> **Persona:** repo maintainer (dogfooding operator)

## User Story

**As a** repo maintainer deciding whether to add the next guard
**I want** a per-commit gate budget set against the improved baseline
**So that** growth is measured against a number someone chose, instead of every new guard being
individually justifiable forever

## Context

RFC0048 D6 is resolved as sequenced-not-numbered: set the budget AFTER option B lands, so the
number ratifies an improved baseline rather than today's bloat. This story closes it, and
therefore depends on the other three.

The RFC's standing risk is not hypothetical. Between 19 and 21 July, `test_gate.py` grew from
56.4s to 72.2s - 28% - while gaining three tests, and nobody noticed until it was measured
again. A budget reported only as an instantaneous pass or fail would not have surfaced that, so
the check reports the trend against a dated baseline.

## Acceptance Criteria

### AC1: the budget is a number a human chose, recorded with its baseline

- **Given** the measured suite and gate times after the other three stories land
- **When** the budget is written to config
- **Then** it carries the measured baseline and the date it was set against, so a later reader
  can tell what the number was a judgement about
- **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLaneTests::test_budget_config_carries_its_baseline
- **Verified:** yes (2026-07-21)

### AC2: the report shows drift, not just the current value

- **Given** a measured gate time and the recorded baseline
- **When** the lane reports
- **Then** it names the baseline and its date alongside the current value, so a 28% drift is
  visible as drift rather than as a still-passing number
- **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLaneTests
- **Verified:** yes (2026-07-21)

### AC3: over budget warns and never blocks

- **Given** a measured time over the budget
- **When** the lane runs
- **Then** it warns and the gate is not refused, so a slow or loaded machine cannot block a
  correct commit
- **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLaneTests::test_over_budget_warns_and_never_blocks
- **Verified:** yes (2026-07-21)

### AC4: D6 is closed with the number and its baseline

- **Given** RFC0048's decision table
- **When** the budget is set
- **Then** D6 is marked Resolved with the chosen number and the baseline it was measured against
- **Verify:** manual confirm D6 reads Resolved with the number at delivery. Not executable: a
  grep for the row cannot tell a resolved decision from the word appearing in prose.
- **Verified:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
