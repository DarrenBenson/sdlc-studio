# EP0355: A team declares a monthly budget and sees its spend against it

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0716
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0716. Delivers the work CR0716 requested.

## Story Breakdown

- [ ] [US1269: The sprint report shows month-to-date spend against a declared monthly budget across every harness](../stories/US1269-the-sprint-report-shows-month-to-date-spend.md)
- [ ] [US1270: The PRD, the Primary persona card and RFC0063 state the monthly budget's true status](../stories/US1270-the-prd-the-primary-persona-card-and-rfc0063.md)

## Acceptance Criteria (Epic Level)

- [ ] A config key lets a project declare a monthly budget in money, documented in reference-config.md with its default of unset
- [ ] The sprint report shows month-to-date spend against the declared budget across every harness that ran work, and says no budget is declared when the key is unset
- [ ] The PRD inventory carries a row for the monthly budget with an honest status, and O11 is marked Partial until that row is Complete
- [ ] RFC0063's Decomposed-into list names this CR as the budget view its fifth workstream planned

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
