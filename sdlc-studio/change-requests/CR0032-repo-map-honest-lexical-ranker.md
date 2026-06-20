# CR-0032: redocument repo_map as a lexical relevance ranker (RFC0004)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Autosprint (RFC0004)
> **RFC:** RFC-0004
> **Date:** 2026-06-20
> **Affects:** reference-repo-map.md, scripts/repo_map.py (docstring)
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0004 (Accepted, Option A(b)). Close the honesty gap: repo_map is
advertised loosely as a "relevance ranker", but its ranking is lexical token-overlap
plus a flat import in-degree bonus - not a semantic call graph or PageRank over a
def->ref identifier graph. Redocument it accurately and point to Aider's repo map /
RepoMapper as the soft dependency for graph-based ranking. No behaviour change
(A(a) PageRank build deferred; reversible if edit-accuracy harm is later shown).

## Proposed Changes

- `reference-repo-map.md`: headline reframed to "lexical relevance ranker"; a new
  "Lexical, not graph-based ranking" limit naming what it does NOT do (no reference
  extraction, edge weighting, personalised PageRank, per-symbol rank, token-budget
  fitting; Python-only AST) and pointing to Aider/RepoMapper as a soft dep.
- `scripts/repo_map.py`: module docstring matches (honesty at source).

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| reference-repo-map.md | accurate framing + soft-dep pointer | Modified |
| scripts/repo_map.py | docstring honesty | Modified |

### Breaking Changes

None. Documentation only.

## Acceptance Criteria

- [x] `reference-repo-map.md` describes repo_map as a lexical relevance ranker and states it is not a call graph / PageRank.
- [x] It points to Aider/RepoMapper as the soft dependency for graph-based ranking.
- [x] `repo_map.py`'s module docstring matches the honest framing.
- [x] Anchor-links and markdown lint pass; the test suite is unaffected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0004) | Complete - honesty redoc (Option A(b)); A(a) PageRank deferred |
