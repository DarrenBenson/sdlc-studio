# US1083: The persona index's history is complete and ordered, it links the seat cards, and the legacy personas.md agrees with its banner

> **Status:** Ready
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/index.md, sdlc-studio/personas.md, tools/tests/test_persona_coherence.py, changelog.d/US1083.md
> **Epic:** EP0289
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading the persona registry to see who a unit serves
**I want** the index's history complete and in date order, the seat cards linked, and the legacy `personas.md` agreeing with its own banner
**So that** the registry is a record I can trust rather than one that contradicts itself

## Acceptance Criteria

- **AC1:** Given the persona index's Revision History, when its dates are read, then they are in ascending order, and every date `git log --date=short` gives for a commit that changed `sdlc-studio/personas/index.md` is one of them
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_history_is_ordered_and_complete
- **AC2:** Given the persona index, when it is read, then it carries a `Last updated` line equal to its latest Revision History date
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_carries_its_last_updated_date
- **AC3:** Given the persona index, when its links under a non-role heading are read, then their targets are exactly the paths `persona_resolve.py resolve --seat <seat> --path-only` prints for engineering, product and qa, and the registry reader returns the same personas it returns without the links
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_links_the_seat_cards_in_force
- **AC4:** Given the legacy `sdlc-studio/personas.md`, when it is read, then it does not contain `primary user`, and its skill-maintainer section links the card of the tooling Primary `primary_cards()` returns
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_legacy_file_agrees_with_its_banner

## Notes

- Serves: Maya Okafor, End goal 4.
- Delivers CR0648:28 (EP0289:31; the consult at :451 and :467). Today the history rows run 07-27, 06-21, 07-16, 10-19; the 2026-07-29 change (cec10acc, BG0307) has no row; there is no Last updated line; :6 names the seats but links none; personas.md:46 says 'primary user' under a banner (:19) saying it records no Primary, and its maintainer section does not link Rowan's card.
- The registry reader registers any bullet under a role heading (sdlc_md.py persona_registry), so the seat links go under a non-role heading; AC3's second clause holds that.
- The consult also asks that the index's singular headings (:8, :16) read for two Primaries. That wording is left to the reviewer's judgement, not a phrase test.
- AC1 must fail on: a history row moved out of order; the 2026-07-29 row missing.
- AC2 must fail on: Last updated left behind the latest row.
- AC3 must fail on: a seat card linked under a role heading, so the reader counts it as a persona.
- AC4 must fail on: line 46 left as it is.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
