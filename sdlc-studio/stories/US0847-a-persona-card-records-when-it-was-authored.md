# US0847: a persona card records when it was authored, from what evidence and when it was last revisited, and every consult figure carries that age

> **Status:** Draft
> **Created:** 2026-09-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/consult.py, .claude/skills/sdlc-studio/scripts/tests/test_consult.py
> **Epic:** EP0256
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator reading a consult's yield figure
**I want** every persona to carry when it was written, from what evidence, and when it was last revisited
**So that** a number measured on personas says what it knows, rather than implying the personas are current

## Acceptance Criteria

RFC0058 D5 is ruled this far (D0213's sibling ruling): provenance and age are recorded, no refresh process is built yet. The point is that a yield figure stops implying more than it knows - a consult's value rests on personas someone authored at a moment, from evidence that may have moved.

### AC1: a persona card carries its provenance, and one that does not is named

- **Given** the three authored persona cards and a fourth with no provenance block
- **When** `persona_resolve.py resolve --seat <role>` renders any of them
- **Then** the render carries the authored date, the evidence it was drawn from and the last-revisited date, and the fourth renders with those fields marked ABSENT rather than omitted
- **Mutant:** omit the block when it is missing - an unprovenanced persona then renders identically to a documented one, which is the state this criterion exists to end
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py::PersonaProvenanceTests::test_a_card_without_provenance_is_named_not_omitted

### AC2: every consult artefact and yield figure carries the age of the personas behind it

- **Given** a consult run against cards authored 400 days ago
- **When** the artefact is written and the yield is reported
- **Then** both carry the oldest card's age in days beside the figures, and the yield's own text states that validity is unmeasured (RFC0058 D5)
- **Mutant:** carry the age in the artefact but not in the yield - the number then travels without the caveat, which is exactly how a measured figure becomes a claim about personas nobody checked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultYieldTests::test_the_yield_carries_persona_age_and_the_validity_caveat

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-17 | sdlc-studio | Created via `new` (deterministic) |
