# BG1666: This repository's seven persona and seat cards carry no Evidence section, so persona_review.py check reports persona-evidence on each

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/personas/graham-doyle-change-approver.md, sdlc-studio/personas/jonah-reyes-team-lead.md, sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, sdlc-studio/personas/seats/qa.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T12:43:36Z

## Summary

After US1055 (run twenty, RUN-01M7VNR0) `persona_review.py` check here prints blocks=0 reported=7: the four persona cards (Graham Doyle, Jonah Reyes, Maya Okafor, Trevor Hale) and the three project seat cards (engineering, product, qa) have no ## Evidence section citing the ids that ground them. The standard reports rather than blocks this rule, but a repository that ships the standard should meet its own report-level rules, and each refine or triage panel here prints owed lines until the cards are reviewed.

## Steps to Reproduce

Run python3 .claude/skills/sdlc-studio/scripts/`persona_review.py` check in this repository: seven 'reported persona-evidence' lines, one per card.

## Proposed Fix

Give each card an ## Evidence section citing the artefacts, decisions or lessons that ground it, then run `persona_review.py` brief and record a PASS for each card so no owed line remains.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: After US1055 (run twenty, RUN-01M7VNR0) `persona_review.py` check here prints blocks=0 reported=7: the four persona cards (Graham Doyle, Jonah Reyes, Maya...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run python3 .claude/skills/sdlc-studio/scripts/`persona_review.py` check in this repository: seven 'reported persona-evidence' lines, one per card.
- [ ] **AC3** The proposed fix lands, pinned by a test: Give each card an ## Evidence section citing the artefacts, decisions or lessons that ground it, then run `persona_review.py` brief and record a PASS for each...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. The seven cards here lack Evidence sections; persona_review reports rather than blocks (blocks=0), and the cards are this repository's own, not shipped. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
