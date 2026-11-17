# BG1535: Two shipped templates define the Served cast differently, and consult stakeholders reads a folder this repo lacks

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/personas/stakeholder-template.md, .claude/skills/sdlc-studio/templates/personas/persona-template.md, .claude/skills/sdlc-studio/reference-consult.md, sdlc-studio/personas/graham-doyle-change-approver.md, tools/tests/test_persona_coherence.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, personas lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/templates/personas/stakeholder-template.md stakeholder-template.md header comment and Cast line (lines 1-20); persona-template.md 'Cast-role variants' (Customer / Served); sdlc-studio/personas/graham-doyle-change-approver.md Quick Reference
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:23:39Z

## Summary

Two shipped persona templates both claim the Customer and Served cast with incompatible shapes and homes. `persona-template.md` makes Served a flat design card in the personas folder with End Goals, while `stakeholder-template.md` (lines 1 to 20) says a Served party is not a design persona and belongs under `personas/stakeholders/` with a machine-readable stakeholder type, Veto Lines and Evidence They Read. No page says which to use. This repository's only Served party, the card `graham-doyle-change-approver.md`, was written on the flat schema, and `sdlc-studio/personas/stakeholders/` does not exist. The consult that decision D0374 requires for any epic changing a persona therefore has no panel to load, because step 1 of the stakeholder review in `reference-consult.md` (line 264) reads only that folder. Past consults were improvised by hand against the design cards. The registry reader skipping the Served heading is already BG1307; this is the separate schema and consult half.

## Steps to Reproduce

1. Read the header comment and Cast line of `.claude/skills/sdlc-studio/templates/personas/stakeholder-template.md`: a Served party is a stakeholder card under `personas/stakeholders/`.
2. Read the Cast role row and the Customer / Served variant in `persona-template.md` in the same folder: Served is a flat design card.
3. List `sdlc-studio/personas/`: there is no `stakeholders` folder, and `graham-doyle-change-approver.md` declares Cast role Served on the flat schema.
4. Read `.claude/skills/sdlc-studio/reference-consult.md` line 264: the stakeholder consult reads all personas from `sdlc-studio/personas/stakeholders/`.
5. Expected: one schema and one home for a Served party, which the consult reads. Actual: two schemas, and the consult's documented source is empty for a repository that has a Served card.

## Proposed Fix

Decide and state one home for the Customer and Served cast. Either make `stakeholder-template.md` the only schema, remove the Customer / Served variant from `persona-template.md` and move this repository's Served card under `personas/stakeholders/` with the stakeholder type comment, Veto Lines and Evidence They Read; or have `reference-consult.md` say the stakeholder consult also loads flat cards whose Cast role is Customer or Served, and say so in both templates. Whichever is chosen, both templates and the consult page must name the same rule. Add a check to `tools/tests/test_persona_coherence.py` that the two templates do not both claim the Served cast with different homes and that every Served card in this repository sits where the consult page says it is read.

## Acceptance Criteria

- [ ] **AC1** Given the shipped `persona-template.md`, `stakeholder-template.md` and `reference-consult.md`, when the three are read, then they name one and the same home and schema for a Customer or Served party, and the consult page's stakeholder review reads that home. Fails on: one template placing a Served party under `personas/stakeholders/` while the other makes it a flat design card, or the consult reading a folder neither template names.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedHomeTests::test_both_templates_and_the_consult_page_name_one_home_for_the_served_cast
- [ ] **AC2** Given this repository's persona cards, when every card declaring the Served or Customer cast is listed, then each sits where `reference-consult.md` says the stakeholder consult reads and carries the schema that home requires. Fails on: `graham-doyle-change-approver.md` sitting outside what the consult loads, so the D0374 consult has an empty panel.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedHomeTests::test_every_served_card_here_sits_where_the_consult_reads

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
