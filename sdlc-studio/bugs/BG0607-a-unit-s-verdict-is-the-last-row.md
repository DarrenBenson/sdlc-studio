# BG0607: A unit's verdict is the LAST row written, so one seat's APPROVE recorded after another seat's REJECT makes a rejected unit read approved

> **Status:** Open
> **Severity:** High
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

- [ ] **AC1** Given a unit with a REJECT from one seat and an APPROVE from another in the same round, when `critic.py show --unit <id>` runs, then it reports the unit as REJECT and names which seats held which position
- [ ] **AC2** Given a unit whose REJECT has been answered by a recorded repair, when the same command runs, then the unit no longer reports as REJECT on the strength of that answered row
- [ ] **AC3** Given a unit with APPROVE from every seat in the round, when the same command runs, then it reports APPROVE, unchanged from today
- [ ] **AC4** Given the transition gate reading a unit with a masked REJECT, when `transition.py set --id <id> --status Done` runs, then it refuses on that REJECT rather than passing on the later APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
