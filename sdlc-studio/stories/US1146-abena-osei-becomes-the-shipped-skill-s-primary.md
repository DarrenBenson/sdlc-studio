# US1146: Abena Osei becomes the shipped skill's Primary and Maya Okafor moves to Secondary

> **Status:** Ready
> **Delivers:** CR0689
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas/abena-osei-head-of-engineering.md, sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/personas/jonah-reyes-team-lead.md, sdlc-studio/personas/rowan-achterberg-skill-maintainer.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, sdlc-studio/personas/index.md, sdlc-studio/prd.md, tools/tests/test_persona_coherence.py, changelog.d/US1146.md
> **Epic:** EP0305
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Abena Osei becomes the shipped skill's Primary and Maya Okafor moves to Secondary
**So that** CR0689 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given `sdlc-studio/personas/abena-osei-head-of-engineering.md`, then it is headed `# Abena Osei`; its Quick Reference rows read Cast role `Primary`, Role `Head of engineering in an audited organisation` and Context `Leads several three-person teams (product owner, engineer, QA) directing agents the organisation already licenses; every release passes a change approval board`; and its `## End Goals` are these six, in order, each on one line: 1 `Every release passes the change board on the evidence the run produced, with no separate write-up`; 2 `Every specification and every change names an accountable person, not 'the agent'`; 3 `Know what each team's delivery costs per point and hold it to a monthly budget, whichever harness a team uses`; 4 `A defect that escapes to production is traced to where it got through, and the mistake is not repeated`; 5 `People who never open a terminal can follow progress without someone translating for them`; 6 `The process stays small enough to serve the work; every step earns its place`. Its `## Evidence` section has one `End goal N:` line per End goal (1: D0436, EP0275 and EP0276; 2: D0436 and RFC0063 WS2, the owner field; 3: D0436, CR0685 and CR0690; 4: D0436, RFC0061 and RFC0063 WS6, the escape loop; 5: D0436 and D0441; 6: D0443) and a closing line for the card itself citing D0436, D0443 and RFC0063. The test holds the six End goals word for word, as `END_GOAL_5` holds Maya's fifth. Fails on: an End goal reworded, reordered, wrapped onto a second line or missing; an End goal with no Evidence line; any id on the card that resolves to nothing.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests::test_the_shipped_primarys_six_end_goals_stand_with_evidence
- **AC2:** Given the persona cards, then Abena's card carries every section a Primary needs (Quick Reference, Who They Are, End Goals, Experience Goals, Behaviours & Context, Frustrations, Scenario) and an `Interface` row that begins `The shipped skill:` and names `.claude/skills/sdlc-studio/` in a code span; Maya's card declares Cast role `Secondary` and carries no `Interface` row; and `validate.py personas` reports nothing for the cast. Both cards change in this one commit. Fails on: Maya's card still declaring `Primary` beside Abena's (two Primaries on one interface, the check's one error); a required section missing from Abena's card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PersonaWellFormedTests::test_shipped_personas_are_well_formed
- **AC3:** Given `sdlc-studio/personas/index.md`, then `## Primary` lists `[Abena Osei](abena-osei-head-of-engineering.md)` first and Rowan Achterberg second, `## Secondary` lists Maya Okafor above Jonah Reyes, and Rowan's bullet says every other unnamed mint names Abena; Rowan's card opens by naming Abena Osei as Primary for the shipped skill and says a unit that touches a shipped path (`.claude/skills/sdlc-studio/`) is judged against Abena; an unnamed mint whose Affects pick no interface names Abena Osei. Fails on: Rowan listed first; Rowan's card still judging a shipped-path unit against Maya; an unnamed mint naming Maya.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests
- **AC4:** Given Maya's and Abena's cards, then Maya's opens with the quote `A specific person, not a type. The Secondary is served fully, but never at the Primary's expense.` and keeps End goals 1 to 5 word for word; each card's `## Boundaries` links every Primary's card and tables `The shipped skill | Abena Osei`, `Repository tooling | Rowan Achterberg` and `Both interfaces | Abena Osei`; Abena's Scenario has one of her teams run `/sdlc-studio sprint --crs Proposed --goal done`, then Abena sign the run with `sprint.py sign`, then the release pass the change approval board on the signed report's evidence with no separate write-up; Trevor's Boundaries names `[Abena Osei](abena-osei-head-of-engineering.md)` as the shipped skill's Primary. The three `test_mayas_*` tests keep their names, which US1081's Verify lines cite: the End goal test reads Maya's card by name, and the commands and Boundaries tests check both Maya's card and the shipped Primary's card. Fails on: an End goal of Maya's reworded; either table naming Maya for the shipped skill or for both; Abena's Scenario signing before the sprint runs; Trevor's card not linking Abena's.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::CardsStateTheRunTests
- **AC5:** Given the PRD's `### Target Users`, then its Primary bullet for the shipped skill reads `**Primary for the shipped skill (the design target):** Abena Osei, head of engineering in an audited organisation, who leads several three-person teams directing the agents the organisation licenses and answers for every release at a change approval board.` and its Secondary bullet reads `**Secondary (served, never at the shipped skill's Primary's expense):** Maya Okafor, a solo founder-engineer who wants a disciplined, trustworthy lifecycle driven by an agent rather than vibe-coding, and the way in for a builder who starts alone; Jonah Reyes, a small-team lead adopting sdlc-studio on an inherited brownfield repo.`, with Rowan's and Trevor's bullets unchanged. Fails on: the shipped-skill label naming Maya; a registry persona the section does not name.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::PrdTargetUsersTests
- **AC6:** Given the index's Revision History, then it gains a row dated the day it is committed whose Change reads `Abena Osei added as the shipped skill's Primary on the operator's pick (D0436), listed first so an unnamed mint names her; Maya Okafor moves to Secondary and is now less well served on her End goal 3, driving a whole batch to done autonomously (D0443 narrowed D0436's list to that one); Rowan's card and line, and Trevor's Boundaries, name Abena as the shipped skill's Primary`; the rows stay in date order and `Last updated` equals the latest row's date. Fails on: no row for the commit's date; `Last updated` left at 2026-11-01.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::RegistryRecordTests
- **AC7:** Given Jonah Reyes's card, then its closing cast lines name Abena Osei as the shipped skill's Primary in place of Maya Okafor, its `- **Primary:**` line pointing at `abena-osei-head-of-engineering.md` and saying Jonah is served, but never at Abena's expense, and a feature that helps Jonah by adding ceremony for Abena is declined; and nothing else on his card changes: his End goals stay word for word against `GOALS_BASE` (7f3e91a9), so O6-O9 keep their citations. Fails on: his card still naming Maya as the Primary; any other line of his card changed.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_jonahs_cast_lines_name_the_declared_primary_and_nothing_else_changes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
| 2026-11-09 | Claude Opus 5.5 (plan approval, D0446) | Jonah Reyes's card gains its cast-line change and joins Affects (the operator's ruling on the product seat's dissent) |
| 2026-11-09 | Claude Opus 5.5 (run nine) | Affects names the unit's changelog fragment, which grooming left out |
