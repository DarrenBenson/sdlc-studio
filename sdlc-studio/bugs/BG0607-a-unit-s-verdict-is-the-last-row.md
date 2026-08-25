# BG0607: A unit's verdict is the LAST row written, so one seat's APPROVE recorded after another seat's REJECT makes a rejected unit read approved

> **Status:** Open
> **Severity:** High
>
> **Re-opened 2026-08-25, and why the fix was withdrawn:** the repair shipped in RUN-01M0WCCG keyed the retraction on the reviewer STRING - a seat may retire its own REJECT and not another's. An adversarial review measured that turning the whole-workspace conformance lane RED: 579/690 conformant against 608/690 at the base ref, 29 non-conformant, 69 units flipping APPROVE to REJECT, on a lane that BLOCKS at `--release`. Confirmed independently before reverting. The cause is that this repository names seats PER ROUND - US0466 carries `qa-seat-ep0171` REJECT and `qa-seat-close-r2` APPROVE - so a legitimate second-round approval by the same seat reads as a different seat and can never retire the rejection.
>
> **A SECOND fix direction was measured on 2026-08-25 and fails identically.** Keying the roll-up on a recorded REPAIR - which is what AC1 asks for in its own words, "any REJECT in the round stands until a repair answers it" - flips the SAME 69 units, because not one of those rejections carries a repair row: every one was answered by a re-review, and the ledger stores no link from that approval to the rejection it answers. Two independent rules, one number.
>
> **The Proposed Fix cannot be computed from what the ledger stores.** It asks to resolve across the seats of the SAME ROUND, and the ledger records no round: both US0466 rows are dated 2026-08-02, and the round appears only inside the reviewer's name. Neither date, seat string nor row order separates a panel recorded together from a re-review recorded later. The defect is real - one seat's APPROVE does mask another's REJECT, measured on three units of RUN-01M0JD1W - but fixing it needs the verdict schema to record either the ROUND a row belongs to or the rejection an approval ANSWERS. Both are changes to the ledger contract rather than to this roll-up, and no rule computed from what is stored today can tell "rejected and never answered" from "rejected, repaired and re-approved". Re-scope before building again.
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01M0JD1W close, 2026-08-24. Eighteen delivery verdicts recorded across three seats; three units with a recorded REJECT print APPROVE from `critic.py show`. The blocking findings behind those REJECTs were real and were repaired, which is how the masking was noticed at all.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py show` and the gates that read it take a unit's standing verdict to be the most recently recorded row. A panel is three seats, recorded one after another, so a unit REJECTed by the engineering seat and APPROVEd by the product seat reads APPROVE whenever the product row happens to be written second. The verdict then depends on the order the recorder was invoked in, not on what the panel found. Both rows are in the log and honest; the roll-up is what is wrong.

## Steps to Reproduce

1. Record a REJECT for a unit from one reviewer. 2. Record an APPROVE for the same unit from a DIFFERENT reviewer. 3. Run `critic.py show --unit <id>`: it prints APPROVE, and the REJECT is invisible to every caller reading the head row. Observed on RUN-01M0JD1W, 2026-08-24: US0671, US0675 and US0676 each carry a seat REJECT from delivery round 2 and each reads APPROVE because the product seat was recorded last. US0674 reads REJECT only because the product seat happened to be the rejecting one.

## Proposed Fix

Resolve a unit's standing verdict across the seats of the SAME round rather than by recency: any REJECT in the round stands until a repair answers it. Report the panel as its members - `US0675 REJECT (qa, engineering) / APPROVE (product)` - so a split panel is visible as a split rather than resolved silently by write order. Keep the per-row log exactly as it is; only the roll-up changes.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_one_seats_approve_does_not_retire_anothers_reject
- [ ] **AC2** Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its own mind, and refusing that would make every REJECT permanent and a round-two approval unrecordable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::LedgerRollupTests::test_a_seat_may_retire_its_own_reject

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py`, return the last live row from `verdict_for` instead of an unanswered REJECT | Given a unit with a REJECT from one seat and an APPROVE from another, when the standing verdict is read, then it is the REJECT - a panel is several seats recorded one after another, and taking the last row written made the verdict a fact about the order the recorder was called in |
| AC2 | in `critic.py`, drop the same-reviewer allowance from `verdict_for`, so no later APPROVE retires a REJECT | Given a seat that REJECTED and later APPROVED the same unit, when the standing verdict is read, then it is the APPROVE - the paired control and the boundary: a seat may change its own mind, and refusing that would make every REJECT permanent and a round-two approval unrecordable |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
