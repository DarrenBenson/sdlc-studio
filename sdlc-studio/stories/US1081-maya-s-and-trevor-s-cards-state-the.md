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

- **AC1:** Given Maya's card, when its End goals are read, then End goals 1 to 4 are word for word what they are at commit 7f3e91a9, and End goal 5 reads, on one line, `Keep the process small enough to serve the work - every check earns its keep, and one that catches nothing is retired`
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_end_goals_keep_their_numbers_and_gain_the_fifth
- **AC2:** Given Maya's card, when its code spans are read, then each `script.py verb` span names a verb the shipped scripts accept, none names a path in the tooling Primary's `Interface` row read from that card, and her Scenario's spans name a `sprint` run before `sprint.py sign`
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_card_names_shipped_commands_and_the_sign_step
- **AC3:** Given Maya's card, when its Boundaries section is read, then it links the card of every other Primary `primary_cards()` returns, and carries a table whose rows map each Primary's interface (read from that card's `Interface` row) to that Primary and a unit touching both to the Primary listed first in the persona index, with cells equal to those readings
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_mayas_boundaries_table_the_primary_for_each_interface
- **AC4:** Given Trevor's card, when it is read, then it names `sprint.py sign` and D0213, D0213 resolves, and it links the card of each Primary `primary_cards()` returns
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_trevors_card_names_the_one_signature_and_each_primary

## Notes

- Serves: Maya Okafor, End goal 4 (specs, code and docs in sync).
- Delivers CR0648:26 as EP0289:29 narrows it, with the consult's lines: Maya signs once after the close; her gate-cost line cites a shipped command or is left out; hooks, the gate host, the ssh keepalive and this repository's prerequisites stay on the maintainer's card; her End goals keep their numbers. Trevor: one signature at `sprint sign`, refusing an author or a recorded reviewer (D0213); a per-unit sign-off or a second signature is declined; his objection is adopted on evidence that a Primary's End goal is harmed and declined when it serves only him; he is the Negative on both interfaces. His own End goals are not rewritten.
- End goal 5 is approved (D0383): the process stays small enough to serve the work, from her Experience goal 'Unburdened by ceremony - the process earns its keep'.
- AC1 must fail on: an End goal reworded or renumbered; End goal 5 missing.
- AC2 must fail on: the Scenario left naming no `sprint` command (today it says 'runs an autosprint'); a span naming a repository-only path such as `.githooks/`.
- AC3 must fail on: a Boundaries section with no link to the other Primary's card; the mixed-unit row naming the tooling Primary (the rule reversed).
- Goal review amendment round, 2026-10-21 (qa): End goal 5's words are fixed in AC1 so the test holds the criterion's text, not the author's; it stays on one line because BG1107 truncates a wrapped End goal. The mixed-unit rule is a table compared with the cards, since D0379 does not state it.
- AC4 must fail on: Trevor's card left without the signature boundary.
- The base is the committed 7f3e91a9, never the run's base ref, which lives only in the gitignored run state and does not exist on the gate host or in CI. Goal review, 2026-10-21 (engineering, product and qa seats) replaced the two prose checks (the `autosprint` token, the Boundaries sentence regex) with ordered spans and a link.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | sdlc-studio | Retitled: was "Maya's and Trevor's cards state the work they now drive: the signed run, the cost of a gate, and the sign-once boundary" |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
