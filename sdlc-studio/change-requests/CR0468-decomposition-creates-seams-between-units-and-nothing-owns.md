# CR-0468: Decomposition creates seams between units and nothing owns them, so a jointly inconsistent batch passes every unit's own acceptance criteria

> **Status:** Complete
> **Decomposed-into:** EP0184
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM close analysis, operator-raised question); agent; skill v5.0.0

## Summary

Refine sizes and verifies each story in isolation and never asks whether story B preserves the property story A established. The result is a batch of individually correct, jointly inconsistent units, and the first place the inconsistency is visible is a review reading the whole diff - by which point the work is done, the sprint is at its close boundary, and the repair is unplanned.

## Impact

Measured on RUN-01KYKVZM. In-lane verification landed and removed the within-unit defect class almost entirely: of 20 majors the previous sprint roughly 17 were mechanically catchable inside a lane, and of 17 majors this sprint essentially none were. The major rate barely moved (0.61 to 0.55 per unit) because a second class of the same size was underneath it. Thirteen of this sprint's seventeen were seam defects between units in one batch, including four directly contradicting pairs: one story reports a ratio while its partner forbids reporting an unmeasured term as zero and the first defeats the second; one story fixes a directory created without its index while its partner derives the tree and reintroduces it; two stories build a criteria floor while a third builds a stated-absence hatch through it; one story writes the carried lesson set while its partner reads it from a different place. Every one of those eight stories passed its own acceptance criteria. A lane reads exactly one unit, so no amount of in-lane rigour can reach this class - review is the first actor in the pipeline that reads two. The cost lands entirely in the review and repair stage, which is the stage the operator asked to shorten.

## Acceptance Criteria

- [ ] Refine computes and reports the seam map for a batch - pairs of units touching the same file, symbol or stated property - and a pair sharing a property with no criterion asserting that property is preserved is reported at plan time, proven by a test written red before the fix over a fixture reproducing the US0529 and US0530 pair
- [ ] The seam map reaches the delivery lane brief and the review brief, so a lane is told which neighbouring property it must not regress, proven by a test asserting the brief content rather than the map's existence
- [ ] The close reports seam coverage beside the points, and a batch that shipped with unowned seams reports them rather than omitting the line, proven by a test written red before the fix

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM close analysis, operator-raised question) | Raised |
