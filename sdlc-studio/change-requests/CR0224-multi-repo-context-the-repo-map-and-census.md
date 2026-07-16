# CR-0224: cross-repo `Depends on:` resolution in audit and sprint plan

> **Status:** Complete
> **Size:** S
> **Target:** v4.1
> **Priority:** Medium
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

**Rescoped 2026-07-13** (see Revision History): this CR was two features wearing one id.
What remains here is the half with an honest deterministic derivation; the PVD-wide merged
edge list moved to an RFC.

The PVD layer already models the multi-repo product, but the context tooling does not follow
it: a cross-repo dependency (service A's story blocked on service B's API) is invisible to
`audit.py`, whose `_unmet_deps` resolves a `Depends on:` referent against the local workspace
only and reports a legitimate cross-repo edge as unresolvable.

The resolver already exists and works. `blocker_sweep.py` (`_manifest_repos`, `_resolve`)
does cross-repo artefact-id resolution today: in-repo first, then across the PVD manifest's
repos, degrading honestly when a checkout is absent. It is trapped inside one script. Lift it
into a shared helper and call it from `audit.py`.

`sprint.py` needs less than it looks: `_topo_order` already documents that out-of-batch
dependencies are ignored and left to the tranche audit, and a cross-repo dependency is
out-of-batch by definition.

## Acceptance Criteria

- [ ] The manifest-aware id resolver is lifted out of `blocker_sweep.py` into a shared lib helper, with `blocker_sweep` refactored onto it and its behaviour unchanged (existing tests stay green)
- [ ] `audit.py` resolves a cross-repo `Depends on:` referent through that helper: a delivered referent in another manifest repo satisfies the dependency instead of reporting `unmet-deps`
- [ ] An absent sibling checkout degrades honestly - a named warning ("manifest repo X not found at <path>"), never a silent pass and never a false block
- [ ] A regression test covers all three cases: resolved in-repo, resolved cross-repo, and sibling-checkout-absent

## Out of Scope (moved to RFC)

`repo map build --pvd` and the merged cross-repo edge list. The indexer's own reference doc
concedes that basename import matching cross-links unrelated packages *within* one repo;
across repos it is strictly worse, and an edge list built on it would ship a confidently
wrong artefact. A declared `provides`/`consumes` contract in the PVD manifest would be
deterministic and honest, but that is a manifest schema change and a design rung.

## Impact

Today a cross-repo dependency either blocks a tranche falsely or is ignored, so a multi-repo
product cannot be planned as one product - the exact case the PVD layer exists to model. The
fix is a refactor of code already proven in `blocker_sweep`.

**Effort:** S

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-13 | Darren | Rescoped to AC2 only (cross-repo dependency resolution, a refactor of the working `blocker_sweep` resolver). The `repo map --pvd` merged edge list is split out to an RFC: it has no honest deterministic derivation, since the edge list would rest on basename import matching that the repo-map reference already documents as unreliable within a single repo. |
