# US1053: persona_review briefs another seat to review a card against the standard and records its verdict against the card's bytes

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/persona_gen.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py, changelog.d/US1053.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1052
> **Persona:** Maya Okafor

## User Story

**As a** Jonah Reyes, holding the team's persona cards to the same discipline as its code
**I want** `persona_review.py brief` to brief a seat other than the card's own to review it against the standard, and `persona_review.py record` to append the outcome to a committed ledger with the reviewing seat, the date and the card's hash
**So that** every card has a visible, dated verdict from a seat that is not the card, instead of a revision-history line saying it was looked at

## Acceptance Criteria

- **AC1:** Given project qa and product seat cards, when `persona_review.py brief --card sdlc-studio/personas/seats/qa.md --seat product` runs, then the brief names the product card to adopt, the standard page, the card under review, each rule `persona_review.py check` reports for that card with its severity, and the record command, while `--seat qa` exits 2 naming the rule that a seat never reviews its own card and prints no brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py::PersonaReviewRecordTests::test_the_brief_frames_another_seat_with_the_cards_findings
- **AC2:** Given that card, when `persona_review.py record --card <qa card> --outcome fail --reviewer "Lena Marsh (product)" --rule persona-evidence` runs, then `sdlc-studio/reviews/persona-reviews.md` gains one row carrying the card's path, its body hash (the card without its generation stamp or reviewed marker), FAIL, the reviewer, product, the date and persona-evidence, and recording again after `persona_gen.py stamp` adds a generation stamp writes the same hash.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py::PersonaReviewRecordTests::test_a_review_is_recorded_against_the_cards_body_hash
- **AC3:** Given a FAIL naming no rule, a rule the standard does not hold, a reviewer naming no `(role)` group, the card's own seat, or a PASS while a blocking rule still fails on the card, when `persona_review.py record` runs, then each exits 2 naming its reason and the ledger is byte-identical.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py::PersonaReviewRecordTests::test_an_unsound_review_is_refused_and_nothing_is_written
- **AC4:** Given a generated seat card still carrying its provisional stamp, when a PASS is recorded for it, then the stamp becomes the dated reviewed marker `persona_gen.py accept` writes, and `persona_gen.py classify` no longer reports it provisional.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py::PersonaReviewRecordTests::test_a_pass_clears_a_generated_cards_provisional_stamp
- **AC5:** Given a recorded review in a project whose cards include Maya Okafor, when `validate.py personas` runs and `sprint.py goal-review brief --goal "Persona Reviews land for Maya"` runs, then neither reads the ledger as a persona card: no warning names it and the goal traces to Maya alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_record.py::PersonaReviewRecordTests::test_the_review_ledger_is_never_read_as_a_persona_card

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief accepts the card's own role, or leaves out the card's mechanical findings so the seat judges without the floor
- AC2 must fail on: the raw file hashed, so a stamp or a reviewed marker reads as a content change, or the Seat cell taken from the card's role instead of the reviewer's
- AC3 must fail on: the PASS-over-a-blocking-rule refusal missing, so a review can pass a card the floor refuses, or the seat read from free text instead of the `(role)` group
- AC4 must fail on: record writes the ledger and leaves the card provisional, so the existing review's accept path and the new record disagree about whether the card was reviewed
- AC5 must fail on: the ledger written under `sdlc-studio/personas/`, where `check_personas` (validate.py:1250), `persona_cards` (sprint.py:9982) and review_prep (review_prep.py:140) glob it as a card named Persona Reviews
- Serves: Jonah Reyes #3.
- Checked at HEAD: the persona review is prose only (reference-persona.md:369-409, a question list ending in `persona_gen.py accept`); nothing records who reviewed a card, when, or at which bytes. `persona_gen._body_hash` (persona_gen.py:41-47) drops only the generation stamp and the reviewed marker; it becomes public as `body_hash`, so review and generation share one hash (LL0016).
- Ledger `sdlc-studio/reviews/persona-reviews.md`, beside the other ledgers: `| Card | Hash | Outcome | Reviewer | Seat | Date | Rules |`, append-only and committed (never .local, LL0029); the tool writes its header on the first record, as critic.py does for its own. The panel's probe showed a ledger under personas/ is read as a card by three readers (AC5).
- The seat is the first `(<role>)` group in the reviewer string, read through `critic.recorded_seat` once the author-seat story lands (the same rule US1030's footer writes); the role must be one some card declares (`persona_resolve.seat_roster`).
- A seat card is reviewed by any seat but its own; a user persona card by any seat. Context-level independence needs the transcripts US1014 and US1015 read (later).
- `--from-verdict <file>` reads OUTCOME and FAILED lines from the reviewer's own file, as `critic.py record` does. AC3's five refusals are one test with a subTest each.
- Rewrites reference-persona.md's `persona review` workflow in place to run brief then record; its step 5 (clearing provisional labels) becomes what a PASS does. Regenerate the reading guide and reference-scripts-surface.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
