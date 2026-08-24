# CR-0554: A plan row whose recorded kill node is not the criterion's own verifier is undetectable, though the ledger already holds both facts

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. Six rows across US0671, US0674 and US0676, each recorded `killed` by `plan_execution` and each surviving its own criterion's verifier. Filed as BG0606.
> **Date:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`mutation.plan_execution` joins Test Plan rows to the ledger on (criterion, row) and reports `killed` when a kill exists. It never asks WHICH test did the killing. The ledger records that node, and the criterion's `Verify:` line names the node that is supposed to do it, so a row killed only by a test no criterion names is a fact the tooling already holds and does not surface. A criterion then reads as covered while its own verifier would survive the declared mutant.

## Impact

Every project using the test-plan gate. A row that reads `killed` is the strongest evidence this toolchain produces, and it can be produced by a test the criterion does not name. An independent plan review found SIX such rows in one six-unit batch - the batch whose sprint goal was that a unit's own evidence must be honest - and found them by hand, reading the ledger against the Verify: lines. Nothing in the toolchain reports it.

## Acceptance Criteria

- [ ] Given a plan row whose ledger kill node is not named by its criterion's `Verify:` selector, when `plan_execution` reports that row, then its verdict is `killed-elsewhere` and names both the node that killed it and the node the criterion asked for
- [ ] Given a plan row whose ledger kill node IS named by its criterion's `Verify:` selector, when `plan_execution` reports that row, then its verdict is `killed`, unchanged from today
- [ ] Given a criterion whose `Verify:` line names a whole file rather than a node, when a row under it is reported, then the comparison is made at file granularity rather than reported as a mismatch
- [ ] Given this repository's corpus, when the check is run over every unit with a test plan and a ledger, then the count of `killed-elsewhere` rows is recorded as a measured yield rather than asserted

## Recommendation

Option 1 first, then option 2 once the yield is known. This repository's own precedent is `revert-check`, which shipped advisory at the boundary with a yield file so the decision to block would rest on a number. The same shape applies here, and the data needed already exists in sdlc-studio/.local/mutation-runs.json - no new measurement, only a comparison nobody is making.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Raised |
