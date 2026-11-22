# BG1702: critic.py brief --rejoinder checks practices against text that still quotes the prior verdict, so a prior verdict naming a practice satisfies the practices check

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_rejoinder_practices.py, changelog.d/BG1702.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Run twenty-two: the qa reviewer's pre-existing finding on BG1124's round-one diff, and repair lane RC1's hand-back naming cmd_brief's --rejoinder branch
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T11:34:33Z

## Summary

critic.py brief refuses a brief whose checked text names none of the seat's practices. With --rejoinder, the checked text still carries the quoted prior verdict, so a prior verdict that quotes a practice satisfies the check for the new round although the new brief's own text names none. BG1124 narrowed the checked text for the embedded unit diff; the rejoinder quote is the same class and was left.

## Steps to Reproduce

1. In a fixture, record a REJECT verdict whose text quotes one of the qa seat's practices. 2. Run critic.py brief --unit <unit> --seat qa --rejoinder with a seat card whose own text names no practice. 3. The practices check passes on the quoted verdict's words instead of refusing.

## Proposed Fix

Run the practices and claim-inventory checks over the brief's own sections only, excluding the quoted prior verdict as the embedded diff is excluded, and pin it with a fixture whose only practice word is in the quoted verdict.

## Acceptance Criteria

- [ ] **AC1** Given a recorded REJECT verdict whose text names one of the seat's practices and a seat card naming none, when `critic.py brief --unit <unit> --seat qa --rejoinder` runs, then the practices check refuses the brief. Fails on: the quoted prior verdict's words satisfying the check.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_rejoinder_practices.py::RejoinderQuoteDoesNotSatisfyTests
- [ ] **AC2** Given a seat card that does name a practice, when the same rejoinder brief runs, then it is issued with the prior verdict still quoted in full. Fails on: the fix dropping the quote from the brief rather than from the checked text.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_rejoinder_practices.py::RejoinderBriefStillQuotesTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Acceptance criteria authored for building in lane C2 |
