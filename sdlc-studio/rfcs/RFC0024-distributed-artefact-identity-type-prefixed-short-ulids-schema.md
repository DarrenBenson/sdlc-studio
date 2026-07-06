# RFC-0024: Distributed artefact identity: type-prefixed short ULIDs (schema v3)

> **Status:** Accepted
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Raised-by:** Dani Okafor (Engineering amigo)
> **Related:** LL0002 (cross-repo artifact-number collisions), CR0167 (implementation), CR0168 (derived indexes), RFC0021 (role-based actor model)

## Summary

Replace sequential artefact ids (`BG0001`) with a type prefix plus short ULID, for example
`BG-01JQK3F8`, filename pattern `BG-01JQK3F8-short-slug.md`. sdlc-studio is moving from a
single-writer tool to a team-based tool for a specific team shape: trunk-based development,
very small human teams (often one), larger agentic teams. Under trunk-based development plus
parallel agent worktrees, concurrent writers are the normal case, not the exception. Sequential
allocation is a coordination point and a merge-conflict generator; it already bites across
repos (lesson LL0002) and the cross-repo guard in reference-cr.md is a workaround, not a fix.

## Context & Problem

Today `next_id.py` and `artifact.py new` allocate the next free sequential number by scanning
the directory. Two agents in separate worktrees on the same trunk both allocate `CR0180`,
and the second merge either collides on the filename or silently duplicates the id. The
same failure appears across repos sharing a CR/RFC namespace (LL0002). As orchestrated
agentic teams become the primary usage shape, every allocation becomes a race.

Design constraints already decided for this version:

- Identity is allocated at creation; triage is a status transition, never an identity event.
- sdlc-studio stays local-first and offline-capable: no network id service, no central broker.
- The ledger must be passively safe under concurrent writes when orchestration fails.

## Goals / Non-Goals

**Goals**

- Collision-free id allocation with zero coordination between concurrent writers.
- Directory listings still sort in creation order (the main practical benefit of sequential ids).
- Stable identity from the moment of creation, so agents can cross-reference an artefact
  before it is triaged.
- A one-shot migration preserving the ordering and audit history of existing artefacts.

**Non-Goals**

- Authority modelling beyond separation of duties (explicitly deferred past this version).
- Any central allocation service or lock file (a coordination point by another name).
- Changing what an id means: it names an artefact, nothing else.

---

## Design Options

### Option A - Type prefix plus short ULID (recommended)

**Approach:** `{TYPE}-{ULID-prefix}`, e.g. `BG-01JQK3F8`; filename `BG-01JQK3F8-short-slug.md`.
ULIDs are timestamp-prefixed, so lexicographic order is creation order: directory listings and
index sorts keep the property sequential numbers gave us. The random suffix makes concurrent
allocation collision-free without coordination. Ids are allocated by `artifact.py new` at
creation, exactly as today.

**Pros:** no coordination point; sortable; offline; allocation stays a pure local operation;
the short form stays readable in prose and commit messages.
**Cons:** longer than `BG0001`; humans lose "the next number" intuition; a truncated ULID
prefix has a theoretical collision window (mitigated by checking the directory on create and
extending the suffix on the rare clash).
**Effort / risk:** M effort; migration is the main risk surface.

### Option B - Unnumbered until triage (rejected)

**Approach:** artefacts are created with a slug only; a sequential number is stamped when a
triager accepts the artefact.

**Pros:** keeps short human-friendly numbers; single writer at triage time.
**Cons:** it moves the collision to triage time rather than removing it - the triage
transition becomes the new coordination point, and agentic triage is itself concurrent. Worse,
it leaves artefacts without stable identity during exactly the window agents most need to
cross-reference them: the burst of filing that follows a review or an audit. "Identity is
allocated at creation; triage is a status transition, never an identity event" is a decided
boundary, and this option violates it.
**Effort / risk:** lower build effort, but structurally wrong for the team shape.

### Option C - Keep sequential ids plus a cross-repo/worktree reservation protocol (rejected)

**Approach:** keep `CR0180`-style ids and add a reservation file or branch-scoped ranges.

**Pros:** no visible change for users.
**Cons:** every variant is a distributed-locking scheme in a markdown repo; reservation state
itself merges and conflicts; offline worktrees cannot reserve. Complexity lands in the worst
place (the allocator every agent touches).
**Effort / risk:** deceptively high; rejected.

---

## Recommendation

Option A. It is the only option that removes the coordination point rather than relocating
it, and the timestamp prefix recovers ordering, which is the only thing sequential numbers
were actually buying.

## Design Details (to be ratified with the option)

- **Migration:** a one-shot script maps existing ids to ULIDs generated from each file's
  creation date, so migrated artefacts sort in their historical order. Old ids are retained
  as `aliases:` in frontmatter; inbound links keep resolving via the alias table.
- **Friendly numbers:** optionally allocated at GitHub sync time (issue numbers are a natural
  fit) and recorded as aliases. The ULID remains canonical so the tool stays local-first and
  offline-capable; a friendly number is a projection, never an identity.
- **Schema version:** this is schema v3; `reference-upgrade.md` gains the v2 to v3 path and
  `project upgrade` drives the migration for consuming projects.

## Open Decisions

| # | Decision | Options | Owner | Resolution | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | ULID prefix length (8 chars shown; enough entropy for repo-scale volumes?) | 8 / 10 / full 26 | Dani | **8-char timestamp-prefixed suffix**, with a create-time directory check that extends the suffix on the rare clash. A collision-maths spike in CR0167 WS1 may raise it to 10 before release; the reader accepts any length, so this is not a lock-in. | Resolved |
| D2 | Alias resolution surface: frontmatter-only, or also a generated alias map for link checkers | frontmatter / map | Dani | **Both** - `aliases:` in frontmatter is canonical; `check_links.py` and reconcile consume a generated alias map derived from it (a link checker cannot open every file per reference at scale). The map is derived output, never hand-edited (aligns with CR0168). | Resolved |
| D3 | Do friendly GitHub numbers appear in filenames or frontmatter only | frontmatter only (leaning) | Lena | **Frontmatter only** - the ULID stays canonical in the filename so the tool is local-first and offline-capable; the friendly number is a projection recorded as an alias. | Resolved |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Migration breaks inbound links in consuming projects | Medium | High | Aliases in frontmatter; migration rewrites links it can see; `check_links.py` run is part of the migration gate |
| Mixed-era repos (some ULID, some sequential) confuse tooling | Medium | Medium | Every reader accepts both via the alias table; validate warns on unmigrated ids after upgrade |
| Longer ids degrade readability of indexes and prose | Low | Low | Short 8-char prefix; slug carries the meaning |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | Id generator + `artifact.py` / `next_id.py` / `file_finding.py` switch | CR0167 | RFC acceptance |
| WS2 | One-shot migration script + alias support in readers | CR0167 | WS1 |
| WS3 | GitHub-sync friendly-number aliases | CR0167 (scoped item) | WS2 |

## Decision

**Outcome:** Accepted - Option A (type prefix plus short ULID, schema v3).
**Rationale:** It removes the allocation coordination point rather than relocating it (the
fatal flaw of the rejected unnumbered-until-triage option), and the timestamp prefix keeps
directory listings in creation order - the only property sequential numbers were buying.
Identity is allocated at creation; triage stays a status transition. All three open decisions
resolved on their leanings (8-char suffix, dual frontmatter+map aliases, frontmatter-only
friendly numbers); each is reader-tolerant, so none blocks the build and a spike may refine
D1/D2 before release.
**Spawned CRs:** [CR-0167](../change-requests/CR0167-distributed-artefact-identity-implementation-ulid-ids-migration-aliases.md)
(WS1 id generator, WS2 migration + alias readers, WS3 GitHub-sync friendly numbers). Targeted
for the v4 release (schema-v3 tranche).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Drafted options, rejected unnumbered-until-triage, recommended ULID |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Open decisions resolved on leanings; accepted for v4 |
