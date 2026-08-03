# CR-0454: The sprint close invalidates itself: its own output makes the review stale and each retry pays a full suite

> **Status:** Complete
> **Decomposed-into:** EP0177
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK); agent; skill v5.0.0

## Summary

`sprint close` writes the review anchor and the handoff, which leaves LATEST.md uncommitted, which fails the review-current lane on the next attempt. Committing that paperwork is another change, so the close is chasing a moving target - the tool says so in its own words. Each attempt runs the whole gate including all 4,624 tests, so RUN-01KYHVWK's close took four attempts and roughly 16 minutes of test execution to record a decision that was already made. Filing a finding DURING the close has the same effect: BG0350 was filed by the close and immediately failed it.

## Impact

Who: every sprint close, in every project. What breaks: the close costs several full-suite runs to record paperwork nobody is testing, and an operator watching it sees the tool refuse itself repeatedly for reasons that have nothing to do with the work. It also punishes doing the right thing - filing a finding during a close is exactly the honest behaviour the doctrine asks for, and it extends the close by a full gate.

## Acceptance Criteria

- [ ] An artefact created BY the close - the anchor, the handoff, a finding filed during it - does not count as an unreviewed change against that same close.
- [ ] The close's gate runs once for a given tree state; a retry over an unchanged test-relevant surface reuses the previous verdict rather than re-running it.
- [ ] When the close does refuse, it distinguishes a blocker in the WORK from a blocker it created itself, and names which.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK) | Raised |
