# CR-0631: Persona review: a standard every persona card is held to, and an independent review that blocks a failing card

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-12)
> **Decomposed-into:** EP0287
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/help/persona.md
> **Priority:** High
> **Type:** Feature
> **Size:** L

## Summary

RFC0061 workstream 1 (D7). Define the persona standard (format, evidence for every claim, testable goals, consistency with the declared cast and the other seats, freshness) as a best-practices page, implement it as validate checks, and add a persona review ceremony: an independent seat reviews a new or changed card against the standard, and a card that fails it cannot be resolved into a brief until fixed. Memory problems are reported, not blocked. Runs on every card change and once per release. Folds in CR0623 and CR0625's checks (EP0285) as rules this standard cites; they keep their names.

## Acceptance Criteria

- [ ] A new or changed persona card that fails the standard is refused by `persona_resolve` until fixed, naming each failed rule
- [ ] The persona review runs on every card change and once per release, recorded with the reviewing seat and the outcome

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Stakeholder consult on EP0287 (D0374)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Created via `new` (deterministic) |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |

## Amigo Consult

_Consulted 2026-10-12: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Precision bar for a seat's miss (D0364 ruling 3): the draft sets at least 8 of a fresh 12-pair sample, judged by a seat other than the builder, before the rule ships. Confirm or set another bar.
- Size: the revision is 92 points against the draft's 68 (the operator's two additions are 13; the panel's required changes 11). Confirm 6.2 whole, or apply the cut order in the recommendation.
