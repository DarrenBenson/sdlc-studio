# BG0358: A declared proof obligation can go unmet and the sprint still closes clean

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; predicates mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised at the RUN-01KYJZGZ close); agent; skill v5.0.0

## Summary

The plan-time test strategy for RUN-01KYJZGZ named six units owing mutation-plus-unit proof: BG0345, US0493, US0494, US0495, US0496 and US0501. Zero mutation runs are recorded for the sprint - the run register is empty. All six reached Fixed or Review anyway, both suites were green, the gate passed and the close ran. No lane, gate or close ever compared what the strategy DEMANDED against what the delivery PRODUCED.

The obligation was voided by a decision made for a good reason, which is what makes it worth recording: the delivery lanes were instructed not to mutation-test in the working tree, because a reviewer doing exactly that silently reverted a shipped repair the night before (CR0452). That was correct for tree safety and it removed the strategy's central proof with nothing anywhere to notice the trade.

## Steps to Reproduce

Plan a batch containing a unit the strategy assigns mutation proof. Deliver it with unit tests only and no mutation run. Transition it to a terminal status: it is allowed. Run the gate: it passes. Run the close: it proceeds. Inspect the mutation run register: it holds nothing for the sprint. Nothing at any point compares the declared obligation with the delivered evidence.

## Proposed Fix

At close, compare the strategy's per-unit proof obligations against the evidence actually recorded, and report each unmet one by name. Blocking or advisory is a configuration choice, but silence is not an option - an obligation nothing checks should not be printed as a requirement. A deliberate waiver of an obligation, such as suspending mutation runs for tree safety, must be recordable so the trade is visible rather than invisible.

## Acceptance Criteria

### AC1: A declared obligation nobody discharged is named with its unit at the close

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ProofObligationCoverageTests::test_an_undischarged_declared_obligation_is_named_with_its_unit
- **Verified:** yes (2026-07-28)

### AC2: A fully discharged batch says so, and an underivable strategy reports nothing rather than all-clear

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ProofObligationCoverageTests
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-raised at the RUN-01KYJZGZ close) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery. |
