# CR-0167: Distributed artefact identity implementation: ULID ids, migration, aliases (schema v3)

> **Status:** Proposed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0012](../epics/EP0012-distributed-artefact-identity-schema-v3.md)
> **Priority:** High
> **Type:** Enhancement
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Depends on:** RFC0024 (acceptance)

## Summary

Implement the identity scheme ratified by RFC0024: replace sequential ids (`BG0001`) with a
type prefix plus short ULID (`BG-01JQK3F8`), filename pattern `BG-01JQK3F8-short-slug.md`.
This is schema version 3.

## Motivation

sdlc-studio is becoming a team-based tool for trunk-based development with very small human
teams and larger agentic teams. Concurrent writers in parallel agent worktrees are the normal
case, and sequential allocation is a coordination point and a merge-conflict generator (see
LL0002 for the cross-repo variant already observed in the field). ULIDs are
timestamp-prefixed, so directory listings still sort in creation order, recovering the main
benefit of sequential numbers. Identity is allocated at creation; triage is a status
transition, never an identity event.

## Scope

**In scope**

- ULID generation in `artifact.py new`/`batch`, `next_id.py`, and `file_finding.py`; every
  allocator emits the new format.
- One-shot migration script mapping existing ids to ULIDs generated from file creation dates
  so historical ordering is preserved; old ids retained as `aliases:` in frontmatter; links
  the migration can see are rewritten.
- Alias resolution in every reader (`reconcile.py`, `validate.py`, `transition.py`,
  `status.py`, `check_links.py`) so old ids keep resolving.
- Optional friendly numbers allocated at GitHub sync time, stored as aliases; the ULID stays
  canonical so the tool remains local-first and offline-capable.
- `reference-upgrade.md` v2-to-v3 path; `project upgrade` drives the migration for consuming
  projects.

**Out of scope**

- Any central or networked id allocation.
- Authority modelling beyond what other CRs in this set introduce.
- Changing index derivation (CR0168) or authorship fields (CR0169), though both assume this
  id format once shipped.

## Acceptance Criteria

- [ ] Two `artifact.py new` runs in separate worktrees on the same trunk merge cleanly with
      distinct ids (test simulates concurrent allocation).
- [ ] `ls` order of a migrated directory equals the pre-migration sequential order.
- [ ] Migration of this repo's own workspace (166+ CRs, 25 RFCs, 52 archived bugs, epics,
      stories) completes with `check_links.py` clean and `reconcile.py detect` reporting zero
      drift.
- [ ] Old ids (`CR0164`) resolve via alias everywhere an id is accepted (`transition.py`,
      links, indexes).
- [ ] GitHub sync allocates a friendly number as an alias without touching the canonical id;
      sync round-trip test passes offline (sync skipped, nothing degraded).
- [ ] Schema version stamped as 3; `project upgrade` migrates a v2 fixture project end to end.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| RFC0024 | Must be Accepted before build; this CR implements its chosen option |
| CR0168, CR0169 | Siblings in the foundation tranche; not blocking, but ship in the same schema-v3 release so consuming projects migrate once |

## Effort

**L.** Touches every allocator and reader plus a migration with real blast radius.

## Risk

Migration is the risk concentrate: broken inbound links or reordered history in consuming
projects would damage exactly the audit-trail credibility this schema exists to protect.
Mitigate with aliases, a dry-run mode, and running the migration against this repo (dogfood)
before releasing to consuming projects.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Full scope drafted; blocked on RFC0024 acceptance |
