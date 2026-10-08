# BG1003: critic record refuses a review round the operator authorised past the cap, so the ledger's last word on the unit is a superseded REJECT

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py, changelog.d/BG1003.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** BG0993, 2026-10-08: round 3 under D0352 refused by record; kept verbatim on the bug instead.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T21:13:10Z

## Summary

`critic.py record` refuses any round past `review.max_rounds` ('A unit still rejected at the cap is carried as a known issue, not reviewed again'). An operator may rule a further round anyway (this repository's D0352 and D0353 for BG0993), but nothing lets record take it: there is no flag naming the authorising decision, and the only lever is raising `review.max_rounds` for every unit. Round 3's verdict on BG0993 could not be written, and a round-4 APPROVE could not be either, so the ledger keeps a REJECT the unit has moved past, which the closing review and anything else reading the latest verdict will believe.

## Steps to Reproduce

Record two REJECTs for one unit, then `critic.py record --unit <id> --verdict REJECT ...` a third time: 'record refused ... at the cap of 2'. No option accepts a decision id.

## Proposed Fix

Let record accept a round past the cap when it names an accepted decision that authorises it (`--authorised-by D0352`, checked against decisions.md), recording that decision on the row; refuse otherwise, as now.

## Acceptance Criteria

- [ ] **AC1** `critic.py record` writes a round past the cap when `--authorised-by` names an accepted decision, and the row carries that decision
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py -k authorised_round_past_the_cap_is_recorded
- [ ] **AC2** Without it, or naming no accepted decision, record still refuses at the cap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py -k unauthorised_round_past_the_cap_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
