# US0859: a consult artefact's coverage is the stamped unit list and each verdict row's cast role is read from the persona card

> **Status:** Draft
> **Supersedes:** US0840
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/consult.py, .claude/skills/sdlc-studio/scripts/tests/test_consult.py
> **Epic:** EP0256
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** a reader of a stakeholder consult
**I want** coverage taken from the stamped unit list and each row's cast role read from the persona card
**So that** the anti-persona is identifiable and coverage cannot drift as the tree moves under it

## Acceptance Criteria

Carried VERBATIM from US0840 (criteria AC3, AC4), which was groomed and goal-reviewed before it was split. The words are unchanged so the scope is provably the same as the parent's; what changes is that they are now sized where estimation is reliable.

### AC3: coverage is the stamped unit list, never re-derived from the tree

- **Given** a fixture artefact whose `> **Units:**` line names an epic and two of its stories, in a tree where that epic has since gained a third story and one named story has been deleted
- **When** `consult.py units <path>` runs
- **Then** it returns exactly the two stamped story ids and the epic, the later story is absent, and the deleted id is reported beside the list as unresolvable rather than dropped from it
- **Mutant:** read the epic's children at parse time instead of the stamped line - a consult then silently covers every unit added after it ran, which is the one thing a coverage record exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultParseTests::test_coverage_is_the_stamped_units_line

### AC4: each verdict row's cast role is read from the persona card, so the anti-persona is identifiable

- **Given** a fixture tree carrying three persona cards, one holding `| **Cast role** | Negative |`, and two artefacts naming the same three personas but heading their sections differently - as `## Verdicts` with a free-text perspective column, and as `### Negative (anti-persona) Perspectives`, the two shapes already in `sdlc-studio/reviews/`
- **When** `consult.py parse` runs on both
- **Then** both return the same cast role per persona, read from the card rather than from the document; and a fourth persona named in the artefact with no card in the tree carries cast role `unknown` and is named in the output, never defaulted
- **Mutant:** infer the cast role from the section heading the artefact renders - the two consults already written head that section differently, so on one of them the anti-persona US0842 must count separately is read as an ordinary user
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_consult.py::ConsultParseTests::test_cast_role_is_read_from_the_persona_card

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Split from US0840 (8 points, at the ceiling where estimation reliability falls off) in RUN-01M306PY under D0222. Criteria carried verbatim rather than rewritten, so nothing is silently dropped or widened in the split. |
