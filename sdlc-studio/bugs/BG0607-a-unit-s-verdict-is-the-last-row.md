# BG0607: A unit's verdict is the LAST row written, so one seat's APPROVE recorded after another seat's REJECT makes a rejected unit read approved

> **Status:** Open
> **Severity:** High
>
> **Re-opened 2026-08-25, and why the fix was withdrawn:** the repair shipped in RUN-01M0WCCG keyed the retraction on the reviewer STRING - a seat may retire its own REJECT and not another's. An adversarial review measured that turning the whole-workspace conformance lane RED: 579/690 conformant against 608/690 at the base ref, 29 non-conformant, 69 units flipping APPROVE to REJECT, on a lane that BLOCKS at `--release`. Confirmed independently before reverting. The cause is that this repository names seats PER ROUND - US0466 carries `qa-seat-ep0171` REJECT and `qa-seat-close-r2` APPROVE - so a legitimate second-round approval by the same seat reads as a different seat and can never retire the rejection.
>
> **A SECOND fix direction was measured on 2026-08-25 and fails identically.** Keying the roll-up on a recorded REPAIR - which is what AC1 asks for in its own words, "any REJECT in the round stands until a repair answers it" - flips the SAME units, because not one of those rejections carries a repair row: every one was answered by a re-review, and the ledger stores no link from that approval to the rejection it answers.
>
> **A THIRD direction WORKS, and the two above were nested rather than independent.** An adversarial review refuted the conclusion this note first carried. The ledger already stores a partial round identifier: the `Brief` column, a content hash of the brief the seat was handed (`critic.py:143`), which embeds the seat charter and so cannot conflate two seats - `_seats_whose_brief_matches` at `critic.py:110` exists to read it back. Keying the retraction on a MATCHING FINGERPRINT, with no heuristics, recovers a strict superset of what the reviewer string recovers: measured on this corpus, the reviewer-string rule leaves 81 units with an unanswered REJECT and the fingerprint rule leaves 49, recovering 32 and losing none. US0593 is the shape: `engineering; delivery review subagent; round 1` REJECT and `engineering; final independent pass; RUN-01KZCAJX` APPROVE, different strings, identical fingerprint `b8c97c1ab63b` - the round, stored, today. The review's own run of the conformance lane reports 588/690 under the fingerprint rule against 579/690 under the reviewer string and 608/690 at base.
>
> **So the fix is COMPUTABLE and the earlier note was wrong to say otherwise.** What it costs is not a schema change but an EVIDENCE BACKFILL: the residue the fingerprint rule leaves is largely the case AC1 says must read REJECT - one seat rejecting, a different seat approving, with no recorded repair answering the rejection. Those are real masked rejections, and closing them means recording the repairs that answered them, unit by unit. The first two rules also did not corroborate each other: the repair-keyed rule's unanswered set contains the reviewer-keyed one by construction, so their agreement was guaranteed before either was run, and the agreement is what licensed the schema conclusion.
>
> **Re-scope to: key the retraction on the brief fingerprint, and backfill the residue.** Both halves, or the lane goes red on the units the backfill has not reached.
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

Key the retraction on the BRIEF FINGERPRINT, and backfill the residue. Two halves:

1. A REJECT is retired by a later APPROVE carrying the SAME `Brief` fingerprint. The fingerprint hashes the brief the seat was handed, which embeds the seat charter, so it identifies the seat AND the round without conflating two seats - unlike the reviewer string, which this repository writes differently per round. Measured on this corpus: 81 units carry an unanswered REJECT under the reviewer string and 49 under the fingerprint, a strict superset recovering 32 and losing none.

2. The 49 that remain are largely the case AC1 exists for - one seat rejecting, a different seat approving, and no recorded repair answering the rejection. Those are real masked rejections, not rule failures, and closing them means recording the repair that answered each. Land the roll-up WITHOUT the backfill and the conformance lane goes red on every unit the backfill has not reached, which is what happened when this shipped and was withdrawn.

Report the panel as its members - `US0675 REJECT (qa, engineering) / APPROVE (product)` - so a split panel is visible as a split rather than resolved silently by write order. Keep the per-row log exactly as it is; only the roll-up changes.

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
