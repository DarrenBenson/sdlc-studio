# CR-0216: project upgrade must explicitly ask the operator before switching the id numbering scheme

> **Status:** In Progress
> **Verification depth:** functional (red-then-green: apply/adopt refuse without --confirm with zero writes; adopt stamps schema 3 forward-only renaming nothing, a post-adopt filing mints a ULID and mixed eras reconcile clean; the walk names all three operator answers (full/forward-only/decline) with the multi-team rationale; era-divergence advisory fires on v2-config+v3-ids, silent on forward-only mixes and pure v2; declining leaves a v2 project fully upgraded; suite 1577)
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator-requested. The v2->v3 numbering switch (sequential ids -> ULID) is opt-in via the `schema_version` flag, but the project upgrade flow treats it as just another migration step. Renumbering every artefact id is a project-wide, operator-visible decision (links, muscle memory, external references) - the upgrade must surface it as an explicit question with the trade-offs stated, never a default it quietly applies, and a decline must leave the project fully functional on v2 numbering.

## Acceptance Criteria

- [ ] `project_upgrade` (and the upgrade workflow docs) present the numbering switch as an explicit operator question - what changes, what the flag is, that v2 ids keep working - and proceed only on explicit confirmation
- [ ] Declining the switch completes the rest of the upgrade cleanly on v2 numbering (verified by test)
- [ ] `migrate_v3` invoked headless/non-interactively without an explicit confirmation flag refuses with guidance instead of proceeding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
