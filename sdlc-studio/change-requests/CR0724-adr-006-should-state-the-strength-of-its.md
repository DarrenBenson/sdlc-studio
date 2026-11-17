# CR-0724: ADR-006 should state the strength of its N=5 evidence, its source's failure mode and the right instance count

> **Status:** In Progress
> **Decomposed-into:** EP0362
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, trd lens, survived 3 of 3 refute votes; observed at sdlc-studio/trd.md ADR-006 Context and Consequences (lines 952-975); section 1 Key Decisions bullet (58-61); against sdlc-studio/decisions.md D0014 (line 28) and docs/benchmarks/2026-07-08-n5-run.md:41-43, 95
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:50Z

## Summary

ADR-006 in the TRD is the root justification for every blocking gate, and ADR-007, ADR-010 and ADR-011 inherit it. Its Context says the N=5 benchmark measured that judgement-scaled hygiene is skipped, quoting 10 of 10 escapes against 3 of 5 caught by the mandated arm. The decision it cites, D0014, and the benchmark write-up both say that difference is below conventional significance at five runs per cell, and both record a failure mode of the mandated arm itself: a bad plan propagates, with two of five planners pinning the spec wrongly and the critic approving against the wrong oracle. The ADR's Consequences list only over-firing as a negative, and unlike ADR-010 it does not say how far its evidence reaches. Separately, the Key Decisions bullet at lines 58 to 61 says ADR-006 has four v4 instances and then names three.

## Impact

A reader who rebuilds or challenges the gate design from the TRD takes a five-run result as a settled measurement and never learns that the mandated arm has a recorded failure mode of its own. Maintainers weighing whether a new blocking gate is justified inherit more confidence than the source supports. The miscount in Key Decisions sends a reader looking for a fourth ADR that does not exist.

## Acceptance Criteria

- [ ] ADR-006's Context states that the benchmark ran five times per cell and that the escape difference is reportable but below conventional significance, in words that agree with D0014 in sdlc-studio/decisions.md and with docs/benchmarks/2026-07-08-n5-run.md
- [ ] ADR-006's Consequences name the bad-plan propagation failure mode recorded in D0014 as a negative, beside over-firing
- [ ] The Key Decisions bullet for ADR-006 gives a count of instances equal to the number of ADRs it then lists
- [ ] A test in tools/tests/`test_lean_trd_refresh.py` fails when the instance count in that bullet differs from the number of ADR ids listed after it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
