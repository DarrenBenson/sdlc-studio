# CR-0716: Give outcome O11 its declared monthly budget, or mark the outcome partial until it exists

> **Status:** In Progress
> **Supersedes:** CR0720
> **Decomposed-into:** EP0355
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/prd.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Outcomes, line 112 (O11); no matching row in the Section 3 inventory or the Section 9 flags table
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:31Z

## Summary

PRD outcome O11 reads that each team sees what its delivery costs per point, in money, against a monthly budget it declares, whichever harness ran the work. The cost-per-point half is built, through the price table, the dollar cost row and the multi-harness token meter. The budget half has nothing behind it: no config key declares a monthly budget, no report row compares spend with one, and no feature row in the PRD inventory claims it. The word monthly appears in no shipped script, reference page, help page or config default, and the only budgets shipped are per-run ceilings. RFC0063 plans a monthly team budget view through a new CR that was never filed, so a Sprint Goal can cite O11 as served while half of it is unimplemented and nothing marks it Partial.

## Impact

The head of engineering persona whose third end goal O11 quotes, and any team that plans against it. They cannot declare a monthly budget or see spend against one, and the PRD gives no sign that this half of the outcome is missing, so goals citing O11 overstate what a run delivered.

## Acceptance Criteria

- [ ] A config key lets a project declare a monthly budget in money, documented in reference-config.md with its default of unset
- [ ] The sprint report shows month-to-date spend against the declared budget across every harness that ran work, and says no budget is declared when the key is unset
- [ ] The PRD inventory carries a row for the monthly budget with an honest status, and O11 is marked Partial until that row is Complete
- [ ] RFC0063's Decomposed-into list names this CR as the budget view its fifth workstream planned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
