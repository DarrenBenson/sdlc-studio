# BG1003: critic record refuses a review round the operator authorised past the cap, so the ledger's last word on the unit is a superseded REJECT

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py, changelog.d/BG1003.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/decisions.py
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

Let record accept a round past the cap when it names an accepted decision that authorises it (`--ruling D0352`, checked against decisions.md; not `--authorised-by`, which `critic.py supersede` already uses for a principal), recording that decision on the row; refuse otherwise, as now.

## Acceptance Criteria

- [ ] **AC1** Given a unit at the review cap and an accepted decision that names the unit and authorises a further round, when `critic.py record --ruling <D-id>` writes the next verdict, then the round is recorded and the row carries the decision id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_a_round_authorised_by_a_ruling_naming_the_unit_is_recorded
  - **Verified:** yes (2026-10-13)
- [ ] **AC2** Given the same unit, when record names no ruling, a decision that does not exist, one that is not accepted, an accepted one that does not name the unit, or one already used for an earlier round past the cap on that unit, then it is refused at the cap as now, naming which
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_a_ruling_that_does_not_authorise_this_unit_is_refused
  - **Verified:** yes (2026-10-13)
- [ ] **AC3** Given a ruling that authorises a further round on a unit, when any delivery-verdict writer checks the cap, then it honours the same ruling, because the check lives in `round_refusal` and not in record's argument handling
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_record_past_the_cap.py::RecordPastTheCapTests::test_every_verdict_writer_honours_the_same_ruling
  - **Verified:** yes (2026-10-13)

## Planning notes (goal review, 2026-10-12)

- The flag is `--ruling`: `critic.py supersede --authorised-by` already names a principal (critic.py:839-866), so one flag name would carry two meanings.
- A decision naming several units (D0354 names BG0989 and BG0994 beside BG0993) authorises a round only on a unit it names as authorised, not every id that appears in its text; the test carries a decision that mentions a second unit without authorising it.
- The authorisation belongs in `round_refusal` (critic.py:1520), which every delivery-verdict writer shares.
- When this ships, BG0993's rounds 3 and 4 are recorded under D0352 and D0353, and BG0993 moves to Fixed (D0354).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
| 2026-10-12 | Claude Opus 5.5 (planning) | Goal review: criteria require the ruling to name the unit and to live in round_refusal; flag renamed to --ruling; Points 2 -> 3 |
| 2026-10-12 | Claude Opus 5.5 (planning) | Goal review round 2: one ruling authorises one round on a unit, so a used ruling cannot lift the cap for good |
