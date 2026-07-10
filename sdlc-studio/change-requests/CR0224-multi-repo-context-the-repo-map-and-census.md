# CR-0224: multi-repo context: the repo map and census grow PVD-wide awareness

> **Status:** Deferred
> **Target:** v4.1 (deliberately deferred past the GA tag; operator-directed 2026-07-10)
> **Priority:** Medium
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

v4.1 candidate, from the same vendor white-paper comparison (their 'relational model spanning all applications and dependencies across the enterprise' is genuinely beyond our single-repo scope). The PVD layer already models the multi-repo product; the context tooling does not follow it: `repo_map` indexes one repo, reconcile censuses one workspace, and a cross-repo dependency (service A's story blocked on service B's API) is invisible. Extend repo map to build per-repo maps under a PVD manifest and merge a cross-repo edge list; let sprint plan and the tranche audit read cross-repo Depends on: ids (the numbering is already cross-repo-safe - ULIDs); keep it deterministic and offline (no platform, no server - the maps are committed artefacts).

## Acceptance Criteria

- [ ] repo map build --pvd produces per-repo maps plus a merged cross-repo edge list from the PVD manifest
- [ ] sprint plan and audit resolve cross-repo Depends on: references (warn when the other repo's checkout is absent - degrade honestly)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
