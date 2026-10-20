# EP0289: The persona registry matches the work it serves: a maintainer Primary for the repository tooling, and cards that state current goals

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0648 and re-read against D0379 after the D0374 stakeholder consult (sdlc-studio/reviews/consult-EP0289-stakeholders-2026-10-19.md), which found the breakdown still written for D0373's supplemental card.

**Runs (D0380, D0378):** US1079 lands in the second 6.2 run, first; US1080 to US1083 land in the third. Build order inside the epic: US1079, then US1080 and US1081, then US1082 (it depends on US1081, which may append Maya's End goal 5), then US1083. The stories share files (index.md, Maya's card, test_persona_coherence.py, prd.md), so they are a cluster, not parallel lanes.

## Story Breakdown

- [x] [US1079: A skill-maintainer card is the Primary for the repository-tooling interface, beside Maya as Primary for the shipped skill](../stories/US1079-a-skill-maintainer-card-is-the-primary-for.md)
- [ ] [US1080: A unit is minted against the Primary of the interface its Affects touches, read from interface paths the project declares](../stories/US1080-a-unit-is-minted-against-the-primary-of.md)
- [ ] [US1081: Maya's and Trevor's cards state the signed run, the shipped gate's cost, the sign-once boundary and which Primary governs a mixed unit](../stories/US1081-maya-s-and-trevor-s-cards-state-the.md)
- [ ] [US1082: The PRD's outcome citations name End goals that say them, and Jonah's upgrade goal has an outcome](../stories/US1082-the-prd-s-outcome-citations-name-end-goals.md)
- [ ] [US1083: The persona index's history is complete and ordered, it links the seat cards, and the legacy personas.md agrees with its banner](../stories/US1083-the-persona-index-s-history-is-complete-and.md)

## Acceptance Criteria (Epic Level)

- [ ] A skill-maintainer card is a Primary for the repository-tooling interface and Maya Okafor stays Primary for the shipped skill, each card declaring its interface in an `Interface` row, and the registry, the PRD's Target Users and `validate.py personas` all read the two-Primary cast cleanly (D0379)
- [ ] A unit is minted against the Primary of the interface its Affects touches, read from interface paths the project declares, with a single-Primary cast minting exactly as before and an explicit `--persona` always winning
- [ ] Maya's card states the signed run and the shipped gate's cost (never the repository tooling's), Trevor's card states the sign-once-per-run boundary and how a Negative persona's objection is weighed, and both Primaries' cards say which governs a unit that touches both interfaces
- [ ] PRD outcome O5 cites a Maya End goal that says it, and Jonah's End goal 4 has an outcome, with no maintainer outcome (D0380)
- [ ] The index's history is in date order and complete, carries Last updated, says the registry covers two interfaces and links the seat cards in force; the legacy personas.md no longer contradicts its banner

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Re-read against D0379 after the stakeholder consult: criteria reworded, the run split and build order recorded (D0380) |
