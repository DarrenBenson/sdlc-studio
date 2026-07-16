# CR-0307: A deterministic review-close helper: mint the dated RV, stamp review-state.json, and derive LATEST.md - a review record should never live only in the overwritable anchor

> **Status:** In Progress
> **Decomposed-into:** EP0056
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/review_prep.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16

## Summary

The review close is three mechanical steps the workflow spells out but no script performs: (1) mint the dated RV record, (2) stamp sdlc-studio/.local/review-state.json (reference-review.md marks this CRITICAL, yet it was absent until hand-written on 2026-07-16), (3) rewrite LATEST.md as a derived pointer. Because all three are hand-done, they drift: the sprint-close flow wrote its review INTO LATEST.md with no dated record (near-loss incident), review-state.json had never existed so every artefact read '`last_reviewed`: null', and the anchor is hand-rendered from the template each time. This is exactly the 'never hand-roll what the tooling wires' doctrine gap: the pieces exist (artifact.py new --type review allocates the RV; `review_prep.py` gathers state) but nothing closes the loop.

## Impact

Any review written straight into LATEST.md is one review-run away from destruction: the 2026-07-16 operator-signed sprint-close review existed ONLY in LATEST.md, and the unified review's mandated overwrite would have erased it had the agent not manually preserved it as RV0009.

## Acceptance Criteria

- [ ] A close subcommand (e.g. `review_prep.py` close --rv RVxxxx) stamps review-state.json (per-leg `last_reviewed`, `last_modified`, `review_findings_ref`, reviews.{id} entry) deterministically
- [ ] The unified review workflow and the sprint-close review both require the dated RV file to exist before LATEST.md is rewritten; the helper refuses to derive LATEST.md from nothing
- [ ] reference-review.md step 4 and the close-down ceremony invoke the helper instead of listing hand-steps
- [ ] gate.py's review recency reads the stamped state, so a hand-skipped stamp is visible drift

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
