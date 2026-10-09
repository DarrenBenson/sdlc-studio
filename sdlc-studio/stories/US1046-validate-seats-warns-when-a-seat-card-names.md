# US1046: validate seats warns when a seat card names a persona the cast does not declare in that role

> **Status:** Draft
> **Delivers:** CR0625
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-persona-generate.md, .claude/skills/sdlc-studio/reference-scripts-verify.md, .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py, changelog.d/US1046.md
> **Epic:** EP0285
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose review seats were written for an earlier cast
**I want** `validate seats` to warn when a seat card names a persona the cast does not declare, or declares in a different role
**So that** a product seat cannot give confident verdicts for a Primary the project has demoted

## Acceptance Criteria

- **AC1:** Given a product seat card whose Proficiency line is cold on 'the primary persona (Darren)' and no persona card names Darren, when `validate.py seats` runs, then it warns `seat-persona-unknown` naming the card and that line, and exits 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatCastTests::test_unknown_primary_named_with_card_and_line
- **AC2:** Given a seat card calling Jonah Reyes the Primary persona while `personas/index.md` declares him Secondary and his card's Cast role says Primary, when `validate.py seats` runs, then it warns `seat-persona-role` naming the card, the line and Secondary as the role the registry declares.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatCastTests::test_role_the_registry_does_not_declare_warns
- **AC3:** Given seat cards consistent with the cast, including a claim wrapped across a line break ('the Primary' then 'design persona is Maya Okafor') and the phrase 'a Primary design persona's End goal', when `validate.py seats` runs, then no persona warning is printed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatCastTests::test_consistent_cards_draw_no_persona_warning
- **AC4:** Given the three shipped amigo cards copied in as a project's seats, when `validate.py seats` runs against a cast whose Primary is named Sam, then no persona warning is printed, and against a cast with no Sam the product card's scenario draws `seat-persona-unknown`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::ShippedCardTests::test_shipped_amigo_cards_read_without_false_positives

## Notes

- Release: 6.2 (D0355 breakdown G11, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: no name is extracted after the role phrase, the line number is missing, or the finding is an error that fails the generation flow
- AC2 must fail on: the claimed role is never compared, or is compared with the card's Cast role when the registry is available
- AC3 must fail on: a matcher that reads 'End' after "persona's" as a name, or that matches within one line only and so mis-reads the wrapped claim
- AC4 must fail on: a pattern tuned to the author's own fixtures that misreads the shipped cards' real prose (LL0044 selection bias)
- Serves: Maya Okafor #4.
- A claim is `(primary|secondary|negative)( design)? persona` followed by `is`, a comma, a colon or an opening bracket and then a capitalised name, or `<Name> (Primary)`. It is matched over whitespace-joined text, so a wrapped sentence counts, and reported at the line where the name starts. HTML comments are read (this repo's product card states its Primary in one, seats/product.md:4-5); fenced code is skipped.
- Names resolve on full or first name. The declared role is the registry's (`personas/index.md` via `sdlc_md.persona_registry`), falling back to the card's Cast role only when the registry is unavailable (panel, Q8). A registry-card disagreement is RFC0061 workstream 1's consistency check, not this story's.
- Warnings only: `check_seats` (validate.py:1505) is the error floor of the team-generation flow. RFC0061 D7 decides advisory or blocking; if blocking, this rule becomes the refusal.
- Adds `seat-persona-unknown` and `seat-persona-role` to the reference-persona.md rule table.
- Project cards only; the shipped defaults are examples, and the shipped product card's 'Sam the new shopper' (templates/personas/amigos/product.md:87) is a true positive in any project with no Sam.
- Edits validate.py, so not in parallel with the reader or Serves stories.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G11 after the refine panel's review |
