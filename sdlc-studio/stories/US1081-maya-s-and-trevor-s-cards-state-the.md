# US1081: Maya's and Trevor's cards state the signed run, the shipped gate's cost, the sign-once boundary and which Primary governs a mixed unit

> **Status:** Ready
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, tools/tests/test_persona_coherence.py, changelog.d/US1081.md
> **Epic:** EP0289
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose card the product seat judges her units against
**I want** her card and Trevor's to state the work as it now runs: `sprint` rather than an autosprint, the one signature after the close, the shipped gate's cost, and which Primary governs a unit touching both interfaces
**So that** a review judging a unit against her goals reads the product she uses today

## Acceptance Criteria

- **AC1:** Given Maya's card, when its End goals are read, then End goals 1 to 4 are word for word what they are at the run's base ref, and an appended End goal 5, if any, is numbered 5
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_end_goals_keep_their_numbers_and_words
- **AC2:** Given Maya's card, when every `script.py verb` code span on it is read, then each names a verb the shipped scripts accept, one of them is `sprint.py sign`, none names a path in the tooling Primary's `Interface` row read from that card, and the card does not contain `autosprint`
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_card_names_shipped_commands_and_the_sign_step
- **AC3:** Given Maya's card, when its Boundaries section is read, then it names every other Primary `primary_cards()` returns, and says which Primary governs a unit touching both interfaces in the form the maintainer card's Boundaries test accepts
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_boundaries_name_the_other_primary
- **AC4:** Given Trevor's card, when it is read, then it names `sprint.py sign` and D0213, D0213 resolves in `sdlc-studio/decisions.md`, and it names each Primary `primary_cards()` returns
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_trevors_card_names_the_one_signature_and_each_primary

## Notes

- Serves: Maya Okafor, End goal 4 (specs, code and docs in sync).
- Delivers CR0648:26 as EP0289:29 narrows it, with the consult's lines: Maya signs once after the close; her gate-cost line cites a shipped command or is left out; hooks, the gate host, the ssh keepalive and this repository's prerequisites stay on the maintainer's card; her End goals keep their numbers, because O1-O4 and 29 artefacts cite them. Trevor: one signature at `sprint sign`, refusing an author or a recorded reviewer (D0213); a per-unit sign-off, a second signature, or an approver on a ruling is declined; his objection is adopted on evidence that a Primary's End goal is harmed and declined when it serves only him; he is the Negative on both interfaces. His own End goals are not rewritten.
- Whether Maya's card gains End goal 5 (for PRD O5, which US1082 re-points) is the operator's to approve with this batch. The proposal is a fifth End goal saying the process stays small enough to serve the work, taken from her Experience goal ('Unburdened by ceremony - the process earns its keep') and her Frustration at :51.
- AC1 must fail on: an End goal reworded or renumbered.
- AC2 must fail on: `autosprint` left on the card; a span naming a repository-only path such as `.githooks/`.
- AC3 must fail on: a Boundaries section naming no other Primary.
- AC4 must fail on: Trevor's card left without the signature boundary.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | sdlc-studio | Retitled: was "Maya's and Trevor's cards state the work they now drive: the signed run, the cost of a gate, and the sign-once boundary" |
