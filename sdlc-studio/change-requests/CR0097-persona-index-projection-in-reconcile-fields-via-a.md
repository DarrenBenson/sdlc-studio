# CR-0097: persona index projection in reconcile fields via a canonical persona field

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

**Estimate: 2 points.** The deferred half of CR0082: project the index `Persona` cell too.
It was deferred because persona had no single canonical field in a story (it lives in the
"As a {persona}" prose, risking a BG0032 clobber). Fix the root cause: add a canonical
`> **Persona:**` metadata field to the story template/scaffold, then extend
`reconcile fields` to project it like Title/Points - so the index Persona column is derived,
not hand-kept. Stories without the field leave the cell untouched (BG0032).

## Acceptance Criteria

- [ ] the story template + `new`/batch scaffold carry a `> **Persona:**` metadata field
- [ ] `reconcile fields` projects `Persona` from that field into the index (alongside
      Title/Points); absent field leaves the cell untouched (no clobber, BG0032)
- [ ] the "As a {persona}" prose stays; the metadata field is the canonical projection source
      (documented in reference-scripts.md / the story template)
- [ ] unit tests: persona drift detected + synced, absent-field safe; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
