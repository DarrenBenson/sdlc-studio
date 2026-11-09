# BG1328: `artifact.py new --type story --epic <a Done epic>` leaves the epic Done, so its parent request derives Complete although the new story is Draft, and `refine apply` refuses to add the deferred slice of an already-decomposed request

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** RUN-01M7061X close: US1149, EP0302 and CR0670 (2026-11-09)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:15:18Z

## Summary

Hit closing run nine (2026-11-09). CR0670 was refined into EP0302 for its first slice only (D0435). When US1140-US1142 were Done, reconcile derived EP0302 Done and CR0670 Complete, though CR0670's AC4 and AC5 were deferred. `refine apply --request CR0670 --into EP0302` refused ('already decomposed'), so US1149 was minted with `artifact.py new --epic EP0302`; EP0302 stayed Done and the next `reconcile apply` derived CR0670 Complete again. Both had to be moved back to In Progress by hand.

## Steps to Reproduce

1. Take a request decomposed into an epic whose stories are all Done (the epic derived Done).
2. Mint a Draft story into that epic with `artifact.py new --type story --epic <epic>`.
3. Run `reconcile apply`: the request derives Complete and the epic stays Done.

## Proposed Fix

Reopen a Done epic (and re-derive its parent) when a non-terminal story joins it, and let `refine apply --into` add a slice to an epic its request already decomposed into; pin both.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Hit closing run nine (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Reopen a Done epic (and re-derive its parent) when a non-terminal story joins it, and let `refine apply --into` add a slice to an epic its request already...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
