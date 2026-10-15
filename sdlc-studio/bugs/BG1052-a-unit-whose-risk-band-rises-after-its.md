# BG1052: A unit whose risk band rises after its review is found under-reviewed only at the close

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** US1004 on RUN-01M4R168: rounds 1 and 2 recorded light (briefs 86df0fd9e922, f5c983151c46); after ec108328 widened Affects, `critic.py brief` derives full (879f7d809935) and sprint.seal_bar_unmet reads 'a review at the depth this unit's risk band demands'; D0368 authorised a third round.
> **Created:** 2026-10-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-14T12:21:22Z

## Summary

A review is briefed and recorded at the tier the unit's risk band derives at that moment. When a repair widens the unit's Affects, the band can rise (US1004: three files to five, light to full), and the recorded light-tier APPROVE no longer meets the seal's bar (an independent APPROVE at the depth the band demands). Nothing says so when the repair lands, when the round-2 verdict is recorded, or in status: the gap first appears in the close's known-issues row, after the review cap is spent, so a further round needs an operator decision (D0368 for US1004).

## Steps to Reproduce

Record a light-tier APPROVE on a unit, then widen its Affects so its band derives full: `critic.py record` and `status` say nothing; `sprint.py close --dry-run` names the unit as one the run cannot end over.

## Proposed Fix

Have `critic.py record` refuse or warn when the verdict's tier is below the tier the unit's current band derives, and have `critic.py brief --rejoinder` re-derive the tier and name a rise; name an under-depth APPROVE in status beside the review-coverage advisory.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose band derives full and whose only APPROVE is light, when `critic.py record` writes a verdict on it or `status` runs, then the under-depth APPROVE is named with the tier the band demands.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-14 | sdlc-studio | Filed |
