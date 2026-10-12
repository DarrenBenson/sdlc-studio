# US1054: The shipped product card names no Primary, so a project's copy of it passes the standard after an upgrade

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigos/product.md, .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py, .claude/skills/sdlc-studio/scripts/tests/test_shipped_card_passes_standard.py, changelog.d/US1054.md
> **Epic:** EP0287
> **Points:** 2
> **Depends on:** US1052, US1046
> **Persona:** Maya Okafor

## User Story

**As a** Jonah Reyes, upgrading a project that installed the shipped amigo cards
**I want** the shipped product card to judge its scenario against the Primary persona's End goal without naming a Primary, so a project's copy of it passes the standard
**So that** the upgrade that makes failing cards refuse never refuses a card the skill itself wrote into my project

## Acceptance Criteria

- **AC1:** Given a fixture project upgraded with `project_upgrade.py --apply --with-default-amigos` and a cast with no persona named Sam, when `persona_review.py check` runs, then no blocking rule fires on any of the three copied cards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shipped_card_passes_standard.py::ShippedCardStandardTests::test_an_upgraded_projects_copied_cards_trip_no_blocking_rule
- **AC2:** Given the reworded shipped product card copied into a project, when `validate.py seats` runs, then it reports errors=0 and no seat-persona finding, and the card still carries its Scenario and every review-render section.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shipped_card_passes_standard.py::ShippedCardStandardTests::test_the_reworded_card_keeps_its_scenario_and_review_render

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the shipped scenario keeps 'the Primary persona, Sam the new shopper' (product.md:87), which US1046 AC4 records as a true seat-persona-unknown in every project with no Sam
- AC2 must fail on: the reword drops the scenario or a review-render heading to silence the rule
- Serves: Jonah Reyes #4 (upgrade safely).
- Checked at HEAD: `project_upgrade --with-default-amigos` and the greenfield install's migration (project_upgrade.py:603-668) copy templates/personas/amigos/product.md verbatim into personas/seats/; its scenario (product.md:87) names 'the Primary persona, Sam the new shopper', and the shipped qa card is also held by a Sam.
- The reword: 'Lena checks it against the Primary persona's End goal, "add my first item in seconds" ... marks the story Ready against that goal.' US1046 AC3 pins 'a Primary design persona's End goal' as drawing nothing.
- Revises US1046 AC4's second half in test_validate_seats_cast.py: the shipped cards now draw no persona warning in either cast, and the true-positive case moves to a fixture card carrying the old sentence. US1046 lands first (dependency), so this story changes its test rather than racing it.
- Builds before the refusal story, so no release refuses the shipped card's copy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
