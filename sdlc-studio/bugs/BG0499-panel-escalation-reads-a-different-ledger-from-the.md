# BG0499: panel escalation reads a different ledger from the one review-batch writes, so two REJECT rounds through the CLI notify nobody

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Executed by the independent closing-review pass on US0603 during the RUN-01KYZKY5 close, reproduced through the shipped CLI in a fixture.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`panel_escalation` is consulted only from `cmd_review_batch`, and it decides by calling `critic.unit_review_rounds`, which reads `sdlc-studio/reviews/critic-verdicts.md`. But `review-batch` records into `sdlc-studio/reviews/sprint-review-record.md`. So the two halves of the same command read and write different files: running `sprint review-batch --verdict REJECT` twice on one unit escalates nothing, and a panel that records two REJECTs through `critic.py record` and never runs `review-batch` also notifies nobody. The escalation fires only in the one combination where somebody uses both commands on the same unit.

## Steps to Reproduce

Run `sprint.py review-batch --units US0001 --verdict REJECT` twice against a fixture, then read stdout: no ESCALATED line appears. Record two REJECTs for the same unit with `critic.py record` instead, and no escalation appears either, because nothing calls `panel_escalation` on that path.

## Proposed Fix

Decide which ledger is the review record of a round, and make both halves use it. Then pin the wiring with a criterion that drives review-batch rather than calling `panel_escalation` directly - the round-two pass found that deleting the whole escalation loop leaves all five of US0603's criteria green.

## Acceptance Criteria

- [ ] Two REJECT rounds recorded through the shipped command escalate to the operator, whichever of the two commands recorded them; and deleting the escalation loop from `cmd_review_batch` reddens a criterion.

## Impact

The escalation exists so a twice-rejected or split-panel unit reaches the operator. On the path a user is most likely to take, it is silent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
