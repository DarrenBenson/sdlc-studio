# US1083: The persona index's history is complete and ordered, it links the seat cards, and the legacy personas.md agrees with its banner

> **Status:** Done
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/index.md, sdlc-studio/personas.md, tools/tests/test_persona_coherence.py, changelog.d/US1083.md
> **Epic:** EP0289
> **Points:** 1
> **Depends on:** US1081
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading the persona registry to see who a unit serves
**I want** the index's history complete and in date order, the seat cards linked, and the legacy `personas.md` agreeing with its own banner
**So that** the registry is a record I can trust rather than one that contradicts itself

## Acceptance Criteria

- **AC1:** Given the persona index's Revision History, when its dates are read, then they are in ascending order, and every date `git log --date=short` gives for a commit that changed `sdlc-studio/personas/index.md` is one of them
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_history_is_ordered_and_complete
  - **Verified:** yes (2026-11-01)
- **AC2:** Given the persona index, when it is read, then it carries a `Last updated` line equal to its latest Revision History date
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_carries_its_last_updated_date
  - **Verified:** yes (2026-11-01)
- **AC3:** Given the persona index, when its links under a non-role heading are read, then their targets are exactly the paths `persona_resolve.py resolve --seat <seat> --path-only` prints for engineering, product and qa, and the registry reader returns the same personas it returns without the links
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_index_links_the_seat_cards_in_force
  - **Verified:** yes (2026-11-01)
- **AC4:** Given the legacy `sdlc-studio/personas.md`, when each persona section's `**Role:**` field below its banner is read, then none names a role from the index's role vocabulary (read from the index's role headings), and its skill-maintainer section links the card of the tooling Primary `primary_cards()` returns
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests::test_the_legacy_file_agrees_with_its_banner
  - **Verified:** yes (2026-11-01)

## Notes

- From US1080's review (2026-11-01): sdlc-studio/personas/index.md:14 still says 'Listed second, so a story minted with no persona still names the shipped skill's Primary'. Since US1080, an unnamed mint follows the interface its Affects touch (a `.githooks/` unit mints Rowan Achterberg), so that sentence is false; correct it in this unit, which already owns index.md.
- Serves: Maya Okafor, End goal 4.
- Delivers CR0648:28 (EP0289:31; the consult at :451 and :467). Today the history rows run 07-27, 06-21, 07-16, 10-19; the 2026-07-29 change (cec10acc, BG0307) has no row; there is no Last updated line; :6 names the seats but links none; personas.md:46's Role field says 'primary user' under a banner (:19) saying it records no Primary, and its maintainer section does not link Rowan's card.
- The registry reader registers any bullet under a role heading (sdlc_md.py persona_registry), so the seat links go under a non-role heading; AC3's second clause holds that.
- The consult also asks that the index's singular headings (:8, :16) read for two Primaries; that wording is the reviewer's to judge.
- AC1 must fail on: a history row out of order; the 2026-07-29 row missing.
- AC2 must fail on: Last updated behind the latest row.
- AC3 must fail on: a seat card linked under a role heading.
- AC4 must fail on: line 46's Role field left as it is. Goal review, 2026-10-21 (engineering, product and qa seats) (qa, engineering) replaced the `primary user` phrase test with the Role fields read against the index's vocabulary.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
| 2026-10-31 | Claude Opus 5.5 | Run-four plan (D0392): depends on US1081, which shares a file this unit declares |
| 2026-11-01 | Claude Opus 5.5 | Note from US1080's review: the index sentence on the unnamed-mint default is now false |
