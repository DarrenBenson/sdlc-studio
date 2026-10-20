# US1079: A skill-maintainer card is the Primary for the repository-tooling interface, beside Maya as Primary for the shipped skill

> **Status:** Done
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, sdlc-studio/personas/index.md, sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/prd.md, tools/tests/test_persona_coherence.py, changelog.d/US1079.md
> **Epic:** EP0289
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer, who runs this repository's hooks, gate and CI and forward-ports the skill
**I want** a persona card of my own, Primary for the repository-tooling interface beside Maya as Primary for the shipped skill
**So that** repository-only work is designed and reviewed against goals it actually serves, and Maya's name means the skill she installs

## Acceptance Criteria

- **AC1:** Given the registry, when it is read, then it holds two Primaries, Rowan Achterberg for the repository-tooling interface and Maya Okafor for the shipped skill, each card declaring its interface in an `Interface` Quick Reference row and its `Cast role` as Primary, in agreement with the index, and `validate.py personas` reports no error and no undeclared-interface warning (D0379)
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_each_primary_declares_a_distinct_interface
  - **Verified:** yes (2026-10-19)
- **AC2:** Given a story minted with no `--persona`, when it is created, then it names Maya Okafor, the shipped skill's Primary, exactly as before: Maya is listed first under `## Primary` and a test pins that order until US1080 resolves the default by interface
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_an_unnamed_mint_still_defaults_to_the_shipped_skills_primary
  - **Verified:** yes (2026-10-19)
- **AC3:** Given the PRD's Target Users and the index, when they are read, then both name the maintainer as Primary for an interface that does not ship, the index preamble says the registry covers two interfaces, and the PRD names no outcome for the maintainer (D0380)
  - **Verify:** pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests::test_target_users_says_which_interface_each_primary_serves
  - **Verified:** yes (2026-10-19)
- **AC4:** Given the maintainer card, when it is read, then every id it cites anywhere resolves to an artefact, a decision or a lesson, each End goal has an Evidence line, and it states the boundary as one rule: a unit touching a shipped path is judged against Maya, and the maintainer's want is met in repository-only surface
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_the_maintainer_cards_evidence_resolves_and_states_the_boundary
  - **Verified:** yes (2026-10-19)
- **AC5:** Given the maintainer card's End goals, when a reviewer reads them, then each names an outcome a unit can fail against, never a mechanism that merely exists
  - **Verify:** manual: the independent review of this unit judges each End goal against this criterion; no test can tell an outcome from a mechanism
  - **Verified:** manual (2026-10-19) - met, judged by this unit's independent QA review in round 2 (qa-seat-US1079-r1)

## Notes

- AC1 must fail on: either card losing its Interface row, or both declaring the same interface (validate errors on that).
- AC2 must fail on: Rowan listed first under `## Primary`, which silently makes every unnamed mint his (`PersonaRegistry.primary` returns the first bullet; the consult confirmed it by fixture).
- AC3 must fail on: the PRD's Target Users left without the maintainer (the existing `test_target_users_names_every_declared_persona` already fails then), or a maintainer outcome added to `## Outcomes`.
- AC4 must fail on: a cited id anywhere on the card that resolves to nothing, an End goal with no Evidence line, or the boundary rule reversed or half-removed. AC5, an End goal phrased as machinery ('a gate exists'), is judged by the review, since no test can tell the two apart (round 1 of this unit's review).
- Consult folds (consult-EP0289-stakeholders-2026-10-19.md): prd.md joins Affects because the coherence test reds without it; the card is written to EP0287's standard (Evidence section, End goals a Verify can attach to later); the gate-cost and prerequisite frustrations with their figures go on this card, never Maya's; Maya's card gains only its Interface row here; one footer line says outside contributors share the interface; the card does not name the real operator.
- End goals, in order: a push is judged against exactly the commit pushed in minutes the work can absorb (D0366, D0370); a fix landed here is in force in the installed copy the same day (forward-port); a release ships that a consuming team can upgrade to (D0375; Jonah's End goal 4 depends on it); main is never left red and unread (D0181).
- After this lands, US1075-US1078 and US1084-US1086 are repointed at this card before their reviews (D0380), and recorded in each one's revision history.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Groomed after the D0374 stakeholder consult: Primary under D0379, prd.md in Affects, the index order pinned, re-pointed 3 (D0380) |
| 2026-10-19 | Claude Opus 5.5 | Repair after the round-1 REJECT: AC1 names the Cast role, AC4's unoracled clause becomes the manual AC5, the boundary is checked as one rule |
| 2026-10-19 | Claude Opus 5.5 | AC5's stamp corrected to manual, recording the round-2 review that judged it met: the repair had inserted AC5 above AC4's own stamp |
