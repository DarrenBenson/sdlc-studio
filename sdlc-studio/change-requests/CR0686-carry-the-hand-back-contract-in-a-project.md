# CR-0686: Carry the hand-back contract in a project's own seat cards and in `amigo-template.md`, not only in the shipped default seats

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigo-template.md, sdlc-studio/personas/seats/qa.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_agent_definitions.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** run eight (RUN-01M6RZQZ) US1131 review round 1 ([new]), and the orchestrator's friction log (R8-F3)
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:46Z

## Summary

US1131 put the hand-back contract (commands in the foreground, at most three lines naming unit, outcome and hand-in path, no progress message unless blocked) into the shipped amigo seats and the `sdlc-reviewer` definition. A project's own seat cards override the shipped seats (`persona_resolve.py resolve --seat <s> --path-only` names the one in force), and this repository's `sdlc-studio/personas/seats/qa.md`, the card run eight's review briefs named, has no hand-back section; nor do `engineering.md` and `product.md` beside it, nor `templates/personas/amigo-template.md`, from which a project writes its own card. CR0674 (In Progress) states the contract for the shipped definitions and seat charters; this extends it to the cards that override them.

## Impact

In any project with its own seat cards, this one included, a reviewer briefed with `critic.py brief` gets the contract only from the agent definition it was spawned with, if any, and never from its seat card, so the long hand-backs and background commands the contract exists to stop return wherever a project has customised its seats.

## Acceptance Criteria

- [ ] `templates/personas/amigo-template.md` carries the hand-back section, worded as in the shipped amigo seats
- [ ] `validate seats` warns when a project seat card that overrides a shipped seat has no hand-back section, naming the card
- [ ] This repository's seat cards under `sdlc-studio/personas/seats/` carry the section, and a test fails when the template or a shipped seat loses it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
