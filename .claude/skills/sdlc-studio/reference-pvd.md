# SDLC Studio Reference - Product Vision Document (PVD)

The PVD is the **product layer above the PRD** - it coordinates the repos that together
form one product, and traces each product feature to its owning repo's PRD feature. It
**coordinates and traces, never re-specifies** (RFC0015). One writable master, read-only
everywhere else, kept honest by cross-repo tooling so it cannot rot.

<!-- Load when: the user works with a multi-repo product / runs pvd or product reconcile -->

## When you need it

A single repo never needs a PVD - its PRD is the top. Reach for a PVD when several repos
form one product (shared features, an inter-repo API, coordinated releases) and the
coordination is currently living as stale prose in reviews/handovers.

## Layout

- **One writable master:** `sdlc-studio/product/pvd.md` in a product/anchor repo, owned by
  the **Product Manager** persona (the PRD stays owned by the Product Owner). The Product Manager is
  the review seat that signs the **PVD review leg** ("PVD requirements satisfied") - that leg exists
  only where a PVD does (see `reference-review.md`, `reference-workflow-personas.md#document-owner-seats`).
- **The manifest:** `sdlc-studio/product/manifest.yaml` (from `templates/product-manifest.yaml`)
  lists the child repos by short id + local path + git URL.
- **Read-only projection:** every child repo gets the master read-only (symlink in prod,
  synced copy in dev) - see `pvd sync` (CR0048).

## Workflow {#pvd-workflow}

1. **`pvd create`** - render `templates/core/pvd.md` into the product repo's
   `sdlc-studio/product/pvd.md`. Keep it lean: the sections below the opt-in line (topology
   tree, G1-G5 gates, release coordination) are only for large multi-team products.
2. **Manifest** - list each repo (id / path / url) in `manifest.yaml`.
3. **Feature map** - in §3, map each product feature `PF####` to `<repo-id>:<PRD-feature>`.
4. **`pvd sync`** (CR0048) - project the master read-only into each child repo.
5. **`product reconcile`** (CR0049) - verify the feature map + contracts across the repos.

## Tiering (proportionality)

- **Lean (always):** vision/scope, strategic goals, feature inventory, cross-repo
  dependencies, API contract commitments, risk register, decisions log.
- **Opt-in (large products only):** the master/domain/team PVD tree, G1-G5 governance
  gates, formal release coordination. Delete them if unused - do not carry empty ceremony.

## See Also

| Document | Relationship |
| --- | --- |
| `templates/core/pvd.md` | the tiered PVD template |
| `templates/product-manifest.yaml` | the child-repo manifest |
| RFC0015 | the design rationale (accepted, scoped WS1-3) |
