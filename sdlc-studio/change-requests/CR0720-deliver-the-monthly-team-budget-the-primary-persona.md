# CR-0720: Deliver the monthly team budget the Primary persona's End goal 3 promises, or take it out of the card

> **Status:** Superseded
> **Superseded by:** CR0716
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, sdlc-studio/personas/abena-osei-head-of-engineering.md, sdlc-studio/prd.md, .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at sdlc-studio/personas/abena-osei-head-of-engineering.md End Goals item 3; Scenario paragraph ('what it cost against the team's budget'); Evidence bullet for End goal 3
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:26:47Z

## Summary

The Primary persona card `sdlc-studio/personas/abena-osei-head-of-engineering.md` gives End goal 3 two halves: knowing what each team's delivery costs per point, and holding it to a monthly budget. The card's Evidence line backs only the first half, with model pricing. Its Scenario states as present behaviour that the sprint report shows what the run cost against the team's budget. Nothing in the shipped skill declares or reads a money budget: `sprint_report.py` never uses the word, and the only budgets are token capacity, appetite, agent-start context and the gate's seconds. RFC0063 lists a monthly team budget view to arrive by a new change request, and outcome O11 in `sdlc-studio/prd.md` (line 112) repeats the monthly budget as traced to this goal, yet no change request, bug or epic mentions it. A unit judged against the Primary can be measured on half a goal only, and the other half is owed by nothing in the backlog.

## Impact

The head of engineering the product is designed for is told the close reports cost against a budget she declares, and it does not. Every story that cites End goal 3 is reviewed against a goal half of which cannot be met, and PRD outcome O11 has no delivery path. Until the view exists or the card is corrected, the persona, the PRD and RFC0063 all promise behaviour the product lacks.

## Acceptance Criteria

- [ ] A project can declare a monthly money budget in its configuration, documented in `reference-config.md` with its default and its unit.
- [ ] The sprint report states the run's priced cost against the declared budget for the month, and reads NOT MEASURED with the reason when no budget is declared or the run is unpriced.
- [ ] The persona card's Evidence line for End goal 3 cites the unit that delivers the budget half, and its Scenario describes only behaviour the close performs.
- [ ] If the budget view is declined instead, End goal 3, the Scenario and PRD outcome O11 are reworded to the cost-per-point half alone, in the same change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
| 2026-11-17 | Claude Fable 5.2 | Closed as superseded by CR0716 at the discovery breakdown the operator asked for: CR0716 asks for the same config key and the same sprint report row for a monthly money budget, and both are still unbuilt: grep for monthly finds no shipped script, reference page or config default, and sprint_report.py has no budget row. The CR0716 breakdown carries this request's remainder, the Primary persona card's End goal 3 evidence and Scenario, in its second story, so one request delivers the budget and the other would mint a duplicate key and row. |
