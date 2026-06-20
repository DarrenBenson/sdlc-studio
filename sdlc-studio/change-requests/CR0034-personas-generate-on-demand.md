# CR-0034: personas generate on demand from seeds (RFC0007)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Autosprint (RFC0007)
> **RFC:** RFC-0007
> **Date:** 2026-06-20
> **Affects:** `templates/personas/stakeholders/` (deleted), `templates/personas/team/` (deleted), reference-persona.md, reference-consult.md, help/persona.md, AGENTS.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0007 (Accepted, Option A). The skill shipped 15 complete
fictional-character persona files (~1680 lines of invented backstory) in every
install, when a single `persona-template.md` plus the archetype seed list (role +
one-line disposition) and `persona create` can generate them on demand. Remove the
baked characters; keep the seeds; generate on demand. Deletion followed a confirmed
generator path (per the RFC), not the reverse.

## Proposed Changes

- Delete `templates/personas/stakeholders/**` and `team/**` (15 files); keep
  `persona-template.md`, `persona-index-template.md`, `prompts/`.
- `reference-persona.md#archetypes`: reframe to archetype seeds + generate-on-demand,
  with a migration note; reword the create-workflow "Load archetype" step to
  "generate from the seed + persona-template.md".
- `help/persona.md`: "Archetypes Available / Pre-built" -> "Archetype Seeds"
  (`persona create --from-archetype <slug>`).
- `reference-consult.md`: Load-Persona wording; `AGENTS.md`: drop the brittle
  templates file count.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| templates/personas/stakeholders, team | 15 baked characters removed | Deleted |
| reference-persona.md | seeds + generate-on-demand + migration note | Modified |
| help/persona.md, reference-consult.md, AGENTS.md | reframed to the seed model | Modified |

### Breaking Changes

The 15 pre-built character files are removed. Personas generate on demand via
`persona create --from-archetype <slug>`; the named seeds and slugs are retained.
Consuming projects regenerate any personas they referenced (their own
`sdlc-studio/personas/` are unaffected).

## Acceptance Criteria

- [x] The 15 baked character files are deleted; `persona-template.md`, `persona-index-template.md`, `prompts/` are retained.
- [x] The 15 archetype seeds (role + disposition) and their slugs are retained; `persona create --from-archetype <slug>` remains coherent (help slug list == reference-persona seeds).
- [x] No dangling file/path reference to a deleted persona; no doc still claims they are pre-built (anchor-link check passes).
- [x] Migration note present; CHANGELOG records the removal; independent critic APPROVE (no content loss beyond reconstructible backstory).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0007) | Complete - 15 baked characters removed, generate-on-demand from seeds; critic APPROVE (CHANGELOG + slug-nit fixes applied) |
