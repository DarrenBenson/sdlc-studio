# CR-0634: User personas learn from usage, and a generalisable persona learning can be promoted to the shipped amigos

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-12)
> **Decomposed-into:** EP0287
> **Parent:** RFC0061
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/templates/personas/amigos/, .claude/skills/sdlc-studio/reference-persona.md
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

RFC0061 workstream 4 (D6, D9). After seat memory: user personas (Maya, Jonah, Trevor) keep memory from usage evidence, starting with served-goal outcomes (CR0629, running a persona's testable End goal at the close) and stakeholder feedback (RFC0058). A generalisable learning can be promoted to the skill's shipped amigo cards by a deliberate act through the skill source repository, as `lessons add --global` promotes a lesson, never automatically.

## Acceptance Criteria

- [ ] A user persona's memory records a served-goal outcome as evidence with its run
- [ ] Promoting a persona learning writes only to the skill source checkout and is refused into an installed copy

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
