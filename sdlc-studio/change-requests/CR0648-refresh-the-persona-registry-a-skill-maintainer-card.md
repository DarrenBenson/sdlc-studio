# CR-0648: Refresh the persona registry: a skill-maintainer card (D0373), Maya's and Trevor's cards brought to current work, the PRD outcome citations and the index

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/personas/index.md, sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, sdlc-studio/personas.md, sdlc-studio/prd.md, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** RV0028 findings PER-1, PER-2, PER-6, PER-7, PER-8, PER-9, PER-10; D0373; git log: Maya's card last changed 95103dd8 (2026-07-16), Trevor's c3ca46e9 (2026-06-21); artifact.py:288 defaults an omitted --persona to the Primary.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:48:09Z

## Summary

RV0028's persona leg found no persona stale under the 90-day rule but the cards drifted from the work: no card for the skill maintainer, so repo-only units default to Maya (D0373 rules a supplemental card); Maya's card unrevised for 94 days, without the sign step or the gate-cost and prerequisites frustration current sprint goals trace to, and still saying autosprint; Trevor's card silent on the sign-once-per-run boundary and on how a Negative persona's objection is weighed; PRD O5 citing the wrong Maya goal and Jonah's End goal 4 without an outcome; an index with out-of-order history and no link to the seat cards; and a legacy personas.md that contradicts its own banner.

## Impact

The product seat's trace to a real End goal has nothing to cite for current work, and Maya's reference count is inflated by work she never sees.

## Acceptance Criteria

- [ ] A supplemental skill-maintainer card exists and is indexed, and a unit whose Affects is wholly tools/, .githooks/ or .github/ is minted against it by default (D0373)
- [ ] Maya's card names the sign step and the gate cost and prerequisites frustration and no longer says autosprint; Trevor's card states the sign-once-per-run boundary and that a Negative persona's objection is weighed on its evidence
- [ ] PRD outcome O5 cites a Maya goal that says it, and Jonah's End goal 4 has an outcome
- [ ] The index's history is in date order and complete, carries Last updated and links the seat cards in force; the legacy personas.md no longer contradicts its banner

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
