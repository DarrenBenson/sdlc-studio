# CR-0267: RFC0038 U3: velocity is measured in points, and the docs stop describing a model that no longer exists

> **Status:** Complete
> **Priority:** P2
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-config.md
> **Verification depth:** functional - end-to-end through the public CLI: a 3-unit batch of 3+5+8 points forecasts ~400,000 (16 x 25,000 seed rate), the plan states the rate's provenance and that project evidence replaces it, and retro velocity honestly reports NO measured rate because the four historical sprints predate points. No --effort instruction survives the payload.
> **Depends on:** CR0265
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

The measurement half of RFC0038. Velocity becomes points delivered per sprint - the number that actually planned agile teams use - and the tokens-per-point rate is derived from it rather than assumed.

The retro accuracy table gains the points column, so estimate-vs-actual is finally answering the question a team asks: were the SIZES right? And the docs must stop vouching for a model that has been deleted: reference-sprint.md still describes a complexity-weighted budget and a per-unit estimate summed, both now false, and reference-config.md documents an Effort field that will not exist.

Estimated at 5 points before the work: several files, clear approach, and the docs carry a CI line budget that makes them fiddly rather than hard.

## Impact

The learning loop. Without points in the velocity history, the tokens-per-point rate cannot be re-measured, and the model degrades into the same unvalidated constant this project has now twice deleted.

**Effort:** M

## Acceptance Criteria

- [ ] VELOCITY.md records points delivered per sprint alongside tokens, and the tokens-per-point rate is DERIVED from that history rather than hardcoded.
- [ ] The retro accuracy table carries the points, so estimate-vs-actual reports whether the SIZES were right - not only whether a token number was.
- [ ] A unit delivered above 8 points is flagged in the retro as one that should have been split, and its tokens-per-point is reported against the rest, so the decomposition rule is answerable with evidence each sprint.
- [ ] reference-sprint.md and reference-config.md describe the model that exists: points, WSJF from CoD, a measured rate, and the above-8 decomposition rule. No document vouches for the deleted complexity-weighted forecast or the Effort field.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
