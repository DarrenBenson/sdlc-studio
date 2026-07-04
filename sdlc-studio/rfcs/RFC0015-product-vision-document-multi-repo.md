# RFC-0015: Product Vision Document (PVD) - the multi-repo product layer

> **Status:** Accepted
> **Priority:** High
> **Author:** Darren Benson
> **Date:** 2026-06-21
> **Spans:** sdlc-studio skill (a new top-of-hierarchy artifact + cross-repo tooling), every consuming project in a multi-repo product
> **Related:** RFC0016 (persona engine - the PM persona that owns the PVD), reference-outputs.md, reference-reconcile.md, the existing contract_tables config (CR0008)
> **Supersedes / Superseded by:** --
>
> **Amendment (2026-07-04, CR-0142): WS3 retired.** `product_reconcile` (the feature-map
> traceability check) shipped but never produced a true trace against a real PVD, and its green
> tests hid that; it is removed. WS1/WS2 stand - the PVD, `pvd sync`, and `pvd drift` are the
> working cross-repo tooling. Feature-map integrity is now a `review`-cadence job, not a machine
> check. The design text below is preserved as the original record; read it with WS3 struck.

## Summary

The skill tops out at the **PRD = one repo**, but real products are many repos that
together form a bigger whole (the product spans ~10 repos). Today the cross-repo coordination - shared features,
the API between services, release sequencing - lives as ad-hoc prose in `reviews/` and
`HANDOVER-*` files that go stale. Introduce a **Product Vision Document**: the
product-level artifact **above** the PRD that coordinates the repos, owned by a Product
Manager persona, and - crucially - kept honest by deterministic cross-repo tooling so it
does not become the stale master-spec that classical big-design-up-front died of.

## Context & Problem

Each repo has its own `sdlc-studio/` + PRD and works standalone. Nothing captures: the
**product vision and strategic goals**; the **master feature inventory** (which product
feature is owned by which repo); the **inter-repo dependencies and API contracts** (the
seam where multi-repo products actually break - consuming repo B's federation/TLS/messaging
issues lived exactly here); or **coordinated releases**. Verified twice over: the two repos
already reference each other, but only in handover prose - uncaptured, unchecked,
drift-prone.

## Goals / Non-Goals

**Goals**

- A product-level artifact above the PRD: vision, strategic goals, a master feature
  inventory that **maps each product feature to its owning repo and that repo's PRD
  feature**, cross-repo dependencies, and API-contract commitments.
- Stay true to the thesis: the PVD **coordinates and traces, never re-specifies** (no
  duplicating the PRDs), and a **product reconcile** checks it against the child repos.
- Proportionate: a 2-repo product is not buried in governance; the heavy bits are opt-in.
- One writable master, **read-only everywhere else**.

**Non-Goals**

- A portfolio-management platform / SAFe-in-markdown. Coordination + traceability, not
  program bureaucracy.
- Re-specifying what the per-repo PRDs already own.
- Forcing the product layer on single-repo projects (it is opt-in).

## Design Options

### Option A - Read-only-projected master + cross-repo reconcile (recommended)

One writable **master PVD** in a product/anchor repo (PM-owned); each project gets it
**read-only** in its `sdlc-studio/` (symlink in production, a synced copy in dev), so the
agent and `reconcile` read it locally. A **`product reconcile`** reads the child repos to
verify the feature map (every PVD master feature resolves to a real child PRD feature, and
vice-versa) and the contract commitments. Presence is local; integrity is checked across
repos. **Pros:** every repo sees the vision with no cross-repo access for the common read;
neutral; one source of truth. **Cons:** needs a sync/checksum mechanism + cross-repo reads
for the check.

### Option B - Meta-repo / monorepo aggregation

Pull the product into one repo (submodules or a monorepo) and keep the PVD there.
**Pros:** everything in one place. **Cons:** forces a repo topology on the user; the product is
deliberately multi-repo; high migration cost.

### Option C - Status quo (coordination in prose)

Keep cross-repo coordination in reviews/handovers. **Cons:** the current state - it rots.

## Recommendation

**Option A.** Master PVD in a product/anchor repo, read-only-projected into each project,
with a `product reconcile` that verifies the feature map + contracts against the child
repos. Start **flat** (master + project references) and **lean** (the sections that earn
their place at small scale); defer the domain/team **PVD tree** and the full **G1-G5
governance gates** until a product is genuinely large enough to need them (the
over-engineering lens). The PVD is owned by the **Product Manager** persona (RFC0016);
the PRD stays owned by the **Product Owner**.

### Sections, tiered (from the master-pvd template)

- **v1 / lean (always):** Executive summary + vision; strategic goals/KPIs; master
  feature inventory (feature -> owning repo -> child PRD feature); cross-repo
  dependencies; **API contract commitments**; risk/conflict register; decisions log.
- **Opt-in / large products:** the master/domain/team **PVD topology tree**; the
  **G1-G5 governance stage-gates**; formal release-coordination ceremony.

### The contract layer is the headline

§5 cross-repo dependencies + §6 API contract commitments become **first-class, versioned,
checkable** artifacts. The aim: a cross-repo analogue of `verify_ac` - does what a
producer repo **ships** match what a consumer repo **expects** (mocks/calls)? That seam is
where multi-repo products break, and it is the most differentiated thing here.

## Open Decisions

| # | Decision | Options | Owner | Status |
| --- | --- | --- | --- | --- |
| D1 | Master PVD writable home | dedicated product repo (e.g. `product-vision`) **[leaning]** / designate an existing anchor repo | Operator | Resolved |
| D2 | Read-only enforcement | OS symlink (prod) + sync (dev), with a checksum/version drift check **[leaning]** / convention + check only | Design | Resolved |
| D3 | Feature-map link convention | `PF0003 -> repo-b:F0007` id refs the tooling resolves | Design | Resolved |
| D4 | Contract-check depth in v1 | declare + version + migration-deadline (doc-checkable) now; producer==consumer execution later / full cross-repo contract verify now | Operator | Resolved |
| D5 | Hierarchy depth | flat (master + project refs) **[leaning]** / domain/team tree from the start | Operator | Resolved |
| D6 | Governance gates (G1-G5) | opt-in for large products **[leaning]** / always | Operator | Resolved |
| D7 | Cross-repo access for `product reconcile` | sibling local paths + a repo manifest **[leaning]** / shallow clone of child repos | Design | Resolved |

## Architecture Impact

| Layer | Impact | Change Type |
| --- | --- | --- |
| `templates/core/pvd.md` | the PVD template (tiered) | New |
| `pvd` type + workflows (reference + help) | create/sync/reconcile the product layer | New |
| `scripts/product_reconcile.py` | verify feature map + contracts across child repos | New |
| reference-outputs.md | the PVD sits above the PRD in the hierarchy | Enhancement |
| reference-config.md | the product manifest (child repos + paths/URLs) | Enhancement |
| RFC0016 | the PM persona that owns the PVD | Depends |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| PVD becomes the stale master-spec | High | High | coordinate-not-duplicate + `product reconcile` keeps it true (the whole point) |
| Enterprise bloat (SAFe-in-markdown) | Medium | High | tiered sections; tree + gates opt-in; proportionate to product size |
| Cross-repo read complexity | Medium | Medium | read-only projection for presence; manifest of sibling paths for the check |
| Duplicating PRD content | Medium | Medium | the PVD holds the map + contracts, the PRDs hold the spec; reconcile flags duplication |

## Phased Plan / Workstreams

| WS | Workstream | Becomes | Depends on |
| --- | --- | --- | --- |
| WS1 | `pvd` template (tiered) + the product manifest schema | CR (TBD) | D1, D5 |
| WS2 | Read-only projection (symlink/sync) + version/checksum drift check | CR (TBD) | D2 |
| WS3 | ~~`product reconcile` - feature-map traceability across child repos~~ **RETIRED (CR-0142)** | CR0049 (shipped, then retired) | D3, D7 |
| WS4 | Contract layer: declare/version/migration-deadline + checks | CR (TBD) | D4 |
| WS5 | Cross-repo contract verify (producer ships == consumer expects) | CR (TBD) | WS4 |
| WS6 | (opt-in) PVD topology tree + G1-G5 governance gates | CR (TBD) | D5, D6 |

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC-0016 | Persona engine v2 | Draft | provides the PM persona that owns the PVD |
| Example | -- | the product (two repos first) | -- | the proving instance |

## Decision

> *Filled on acceptance.* Chosen option + rationale + the CRs spawned.

**Outcome:** Accepted, scoped to WS1-WS3 (PVD template + manifest; read-only projection + drift check; cross-repo traceability reconcile). WS4-WS5 (contract layer + producer==consumer verify) and WS6 (PVD tree + G1-G5 governance) deferred.
**Rationale:** The multi-repo coordination gap is real and active; the read-only-projected master + traceability reconcile is the proportionate, build-now core. Contract-verify and governance carry the design/effort risk and wait until the core is in use. Open Decisions resolved to their leanings (D1 dedicated product repo, D2 symlink+sync+checksum, D3 id-ref convention, D5 flat, D7 sibling-paths+manifest); D4 + D6 deferred with their workstreams.
**Spawned CRs:** CR0047 (WS1), CR0048 (WS2), CR0049 (WS3).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - the PVD product layer; home = read-only-projected master (symlink in prod); PM owns it; contract layer the headline; flat + tiered, tree/gates deferred |
| 2026-06-21 | Darren Benson | Decision session: ACCEPTED scoped WS1-3 (spawns CR0047-CR0049); WS4-6 + D4/D6 deferred until the core is in use |
