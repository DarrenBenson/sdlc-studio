# US1052: The persona standard names every rule a card is held to, and persona_review check reports each card against it

> **Status:** Draft
> **Delivers:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/best-practices/persona.md, .claude/skills/sdlc-studio/best-practices/README.md, .claude/skills/sdlc-studio/scripts/persona_review.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/personas/persona-template.md, .claude/skills/sdlc-studio/templates/personas/amigo-template.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py, changelog.d/US1052.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1039, US1046
> **Persona:** Maya Okafor

## User Story

**As a** Jonah Reyes, a team lead who inherited a repository's persona and seat cards
**I want** one written standard for persona and seat cards, and a command that reports each card against it rule by rule, saying which rules block and which are reported
**So that** I can see which inherited cards are fit to brief from before any is trusted, instead of finding a stale card in a reviewer's verdict

## Acceptance Criteria

- **AC1:** Given a fixture project whose seat and persona cards are each built to break one rule, when `persona_review.py check --format json` runs, then every rule it prints appears on `best-practices/persona.md` under exactly one standard heading with its severity (blocks or reported), and every rule the page names is printed for at least one fixture card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py::PersonaStandardTests::test_every_printed_rule_is_on_the_standard_page_and_back
- **AC2:** Given a project seat card carrying a demographic token and a persona card with no Evidence section, when `persona_review.py check --card` runs on each, then the first prints `seat-demographic-fluff` as blocks and exits 1, the second prints `persona-evidence` as reported and exits 0, and `validate.py seats` prints `blocks resolve` beside the first rule from the same table.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py::PersonaStandardTests::test_blocking_and_reported_rules_are_told_apart_from_one_table
- **AC3:** Given a persona card whose Evidence section cites US0001 (a story on disk) and D9999 (in no decisions row), and another whose Evidence cites only ids that resolve to nothing, when `persona_review.py check` runs, then only the second is reported `persona-evidence`, naming its unresolved ids.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py::PersonaStandardTests::test_evidence_must_cite_something_that_resolves
- **AC4:** Given `personas/index.md` declaring Jonah Reyes Secondary while his card's Cast role says Primary, when `persona_review.py check` runs, then it reports `persona-registry-role` as blocks on Jonah's card, naming both roles.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_standard.py::PersonaStandardTests::test_a_card_contradicting_the_registry_blocks

## Notes

- Release: 6.2 (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: a rule added to validate.py or persona_review.py with no line on the page, or a page line naming a rule nothing prints (LL0043: a list checked one way is a lower bound)
- AC2 must fail on: every finding read as blocking, so a card missing only its Evidence exits 1, or none is; or validate keeping its own idea of which rules block (LL0042)
- AC3 must fail on: the rule checks only that an `## Evidence` heading exists, so a section citing nothing real passes (LL0023: a check of existence is satisfied by touch)
- AC4 must fail on: the card's Cast role compared with the other cards (the existing persona-one-primary path) and never with the registry, so the disagreement is only the generic two-Primaries warning HEAD prints
- Serves: Jonah Reyes #3 (hold humans and agents to the same discipline).
- Checked at HEAD a52d5f86: best-practices/ has no persona page; `check_seats` (validate.py:1505) and `check_personas` (validate.py:1226) each print their own rules with no notion of blocking; nothing compares a card's Cast role with `personas/index.md` (fixture probe: Jonah's card set to Primary draws only persona-one-primary's two-Primaries warning, exit 0); no persona or seat card, and neither the persona nor the amigo template, carries an Evidence section.
- The standard's headings: Format, Identity, Evidence, Testable goals, Consistency with the cast, Freshness, Memory hygiene. Each lists the rule names that check it and the questions the reviewing seat answers that no rule can. Rule definitions stay in reference-persona.md's rule table (created by US1039, rows added by US1046); the page cites them by name and never restates them (LL0042). Identity lists US1037's optional `## Goal Review Questions` section, as US1037's notes ask.
- Blocks (D0364: any card, changed or not, no grace mode): seat-unknown-role, seat-no-review-render, seat-demographic-fluff, US1046's seat-persona-unknown and seat-persona-role, and the new persona-registry-role (the registry-card disagreement US1046's notes leave to this workstream). Reported: every other rule, including seat-no-role and seat-duplicate-role (a roleless card is never resolved, persona_resolve.py:83, and the duplicate error sits on the card the lexical-first rule does not resolve, so neither can change what a brief reads), seat-malformed-stamp (it does not mislead a brief), persona-section, persona-cast-role, persona-goal-verify, persona-goal-scope, persona-evidence and the cast-level persona-one-primary, seat-cast-size and seat-core-missing. A rule blocks when it is card-level, deterministic and its failure makes the card mislead a brief; a seat's FAIL review makes any rule block.
- The page states the split's yield (CR0625's consuming-project card arguing for a demoted Primary; US1046's fixtures) and what the refusal retires (persona_resolve's separate RenderError path), as LC-008 asks of a new refusal. It also says the reviewing seat checks each claim on the card, which is how CR0631's 'evidence for every claim' is met above the mechanical floor.
- `persona_review.py check [--card PATH] [--format json]` aggregates check_personas, check_seats and the new rules per card from one rule-to-heading-and-severity table. AC1's test reads the page against it, and `validate.py seats` and `personas` read the `blocks resolve` label from it, keeping their own severity words and exit codes (US1046's warnings stay warnings there).
- persona-evidence: an `## Evidence` section citing at least one id that resolves (an artefact on disk, a decisions row, a lesson in the project or skill registry). The persona and amigo templates gain it, in the bullet shape of stakeholder-template.md's `## Evidence They Read` (a different question: what a stakeholder reads before signing off, not what grounds the card). The shipped amigo cards cite skill lessons.
- This repository's six cards carry no Evidence section, so each is reported persona-evidence until its persona review: reported, never blocking.
- New script `persona_review.py`: persona_resolve is the resolver and persona_gen the generation floor, so the standard, the review and the owed list get one home; persona_gen's hash and accept are reused, not copied.
- reference-persona.md is 522 of its 600-line budget (tools/check_budgets.py); this group adds about 20 lines there (two rule rows, the review workflow rewritten in place, the refusal and owed paragraphs). Memory and learning-loop docs go to the new reference-persona-learning.md, not here.
- Edits validate.py, so not in parallel with US1039, US1043 or US1046. Builds first in the group.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
