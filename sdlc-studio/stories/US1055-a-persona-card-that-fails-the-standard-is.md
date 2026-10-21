# US1055: A persona card that fails the standard is refused at every entry point that resolves it, naming each failed rule and its remedy

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/triage.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, changelog.d/US1055.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1053, US1054, US1036
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, whose reviewers and builders are framed from cards she rarely rereads
**I want** resolve, resolve-consult, the refine and triage panels and critic.py brief to refuse a persona card that breaks a blocking rule or whose latest review failed, naming each rule and the remedy, with no fallback to the shipped card
**So that** a broken or stale card cannot frame a reviewer or a builder, while a card that has merely changed still works and is named as owed its review

## Acceptance Criteria

- **AC1:** Given a project qa seat card carrying a demographic token, when `persona_resolve.py resolve --seat qa` runs with `--render review` and with `--render build`, `resolve-consult --role qa` runs, `critic.py brief --unit US0001 --seat qa` runs and `refine.py apply` and `triage.py` run in dry-run on fixture requests, then resolve and resolve-consult exit 1 and the other three exit 2, each naming the card, seat-demographic-fluff and the remedy, printing no framing or brief and never naming the shipped qa card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py::PersonaReviewBlockTests::test_a_card_breaking_a_blocking_rule_is_refused_at_every_entry_point
- **AC2:** Given a card that passes every blocking rule but whose latest row in the review ledger is a FAIL naming persona-evidence, when the card is edited and `persona_resolve.py resolve --seat qa` runs, then it is still refused naming that review's reviewer, date and rule, and once a PASS is recorded for the edited card it resolves.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py::PersonaReviewBlockTests::test_a_failed_review_holds_until_a_later_review_passes
- **AC3:** Given a card with no review row, and another edited since its PASS, both passing every blocking rule but reported persona-evidence, when `persona_resolve.py resolve --seat qa` runs on each, then each frames the card with exit 0 and prints one stderr line naming the persona review as owed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py::PersonaReviewBlockTests::test_an_unreviewed_card_resolves_and_is_named_owed
- **AC4:** Given `--skip-personas`, and a project with no qa card so the shipped default resolves, when `persona_resolve.py resolve --seat qa` runs with a FAIL row in the ledger for a since-deleted card, then each prints exactly what it prints with no ledger present.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_review_block.py::PersonaReviewBlockTests::test_the_default_card_and_skip_personas_are_untouched

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the refusal raised as a new exception type, so refine.py (:1142) and triage.py (:240), which catch only RenderError, crash with a traceback that still exits non-zero; or the check placed in one entry point only; or a refused card falling back to the shipped default
- AC2 must fail on: the FAIL honoured only while its hash equals the card's current bytes, so any edit escapes the block before a review passes it
- AC3 must fail on: an unreviewed card refused, or a reported rule treated as blocking
- AC4 must fail on: the shipped default judged against the project's ledger, or `--skip-personas` reading the ledger at all
- Serves: Maya Okafor #3 (drive a batch to done, pausing only when a decision is hers).
- Checked at HEAD (fixture probe): a project qa card carrying '42 years old' fails `validate.py seats` (seat-demographic-fluff, error), yet `resolve --render review`, `resolve-consult` and `critic.py brief` all exit 0 on it. refine.py:785 and triage.py:183 resolve the panel in-process and catch only RenderError (refine.py:1142, triage.py:240, both exit 2).
- One function, `persona_review.blocking(root, card)`, called once in US1036's `persona_resolve.review_card` and in `resolve_card` and `resolve_consult` (persona_resolve.py:135, :178), which `amigo_panel`, refine and triage already go through. The refusal is `StandardRefused(RenderError)`, so both in-process callers print it as today; refine.py and triage.py are in Affects for their tests and the refusal text, not a new except clause.
- Retires the separate RenderError message: a missing review render is seat-no-review-render, refused through the same message (LC-008). RenderError's assertions in test_persona_resolve.py move to the new message; exit codes are the ones AC1 pins.
- Every refusal prints the remedy: 'edit the named line of the card, or remove the card to brief from the shipped card for its role; `persona_review.py check` lists every blocked card'. The changelog fragment names the upgrade case (a project card already breaking a card-level `validate.py seats` error, or naming a persona the cast does not declare, stops resolving until fixed) with that remedy. Fragments are consumed at the release cut, so the printed remedy is what AC1 pins.
- D0364: blocks any card failing a blocking rule, changed or not, no grace mode. A card with no review row is not refused; it is owed a review.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1053, US1054 and US1036 (all Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
