# BG1523: The second review seat shipped in 6.4 on the single-sequence round ledger that earlier decisions call unsafe for it

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** sdlc-studio/decisions.md, sdlc-studio/change-requests/CR0622-a-second-different-seat-on-high-risk-units.md, sdlc-studio/change-requests/CR0696-each-unit-carries-a-risk-and-compliance-class.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_second_seat.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 2 of 3 refute votes; observed at sdlc-studio/decisions.md D0341, D0356, D0460, D0474 rows; sdlc-studio/change-requests/CR0622-a-second-different-seat-on-high-risk-units.md (Triage, Amigo Consult); sdlc-studio/change-requests/CR0696-*.md
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:14Z

## Summary

Three accepted decisions disagree and none cites or supersedes another. D0341 rules one reviewer per unit because the verdict ledger numbers rounds by row, D0356 allows a second seat only through CR0622 with per-seat rounds on the ledger, and D0460 then orders a second independent seat on high-risk units with no mention of either or of the ledger. CR0696 delivered that seat in v6.4.0 through US1154, while D0474 deferred the per-seat-round stories US1032 and US1033 to a later release. The code still numbers every verdict on a unit as one sequence in `critic.py`, so with the default cap of two a second seat's REJECT after a first-seat APPROVE is carried at the cap and not repaired, and after a REJECT then an APPROVE the second seat's verdict is refused outright. The ledger defect itself is described in CR0622 and US1032; what is wrong now is that the shipped feature, its CR and the decision record give no sign that it runs without its stated prerequisite.

## Steps to Reproduce

1. Read the D0341, D0356, D0460 and D0474 rows in sdlc-studio/decisions.md: D0460 names neither earlier decision, CR0622 nor the ledger.
2. Read the Triage and Amigo Consult sections of CR0622: a second seat needs a new ledger shape and is recommended only together with per-seat lanes.
3. Read CR0696 and US1154: neither mentions rounds, the cap, CR0622 or US1032.
4. Read `delivery_rounds` (about line 843) and `round_refusal` in .claude/skills/sdlc-studio/scripts/critic.py: one sequence per unit with no seat, and any verdict past the cap is refused.
5. With `max_rounds` at its default of 2, record a first-seat APPROVE then a second-seat REJECT on one unit: the REJECT is round 2 and the unit is carried. Record REJECT, APPROVE, then a second-seat verdict: it is refused.

## Proposed Fix

Record one decision that states how D0341, D0356 and D0460 relate, names the interim behaviour of the second seat on the single-sequence ledger, and marks which earlier rows it supersedes. Cross-reference CR0622 and CR0696, and state the limitation in the second-seat section of the sprint reference so an operator knows a second-seat REJECT is carried and not repaired. Either bring US1032 and US1033 forward or add a refusal with a plain message when a second seat would hit the cap. Pin the stated interim behaviour in the second-seat tests.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Three accepted decisions disagree and none cites or supersedes another.
- [ ] **AC2** The proposed fix lands, pinned by a test: Record one decision that states how D0341, D0356 and D0460 relate, names the interim behaviour of the second seat on the single-sequence ledger, and marks...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
