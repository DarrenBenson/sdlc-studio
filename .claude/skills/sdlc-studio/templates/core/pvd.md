# Product Vision Document: {{product_name}}

> **Document Type:** PVD (master)
> **Version:** {{version}}
> **Last Updated:** {{date}}
> **Status:** {{status}}
> **Owner:** Product Manager ({{pm_owner}})
> **Review Cadence:** {{review_cadence}}

<!--
The PVD is the PRODUCT layer above the per-repo PRD. It COORDINATES and TRACES; it never
re-specifies what a child repo's PRD already owns. One writable master (this file) lives in
the product/anchor repo; every child repo gets it read-only (see `pvd sync`). Keep it lean -
the sections below the "Opt-in" line are only for genuinely large, multi-team products.
-->

## 1. Vision & Scope

**Vision:** {{product_vision}}

**Scope:** {{scope_summary}}

**Business context:** {{business_context}}

## 2. Strategic Goals

| Goal ID | Strategic Goal | Metric | Target | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| {{goal_id}} | {{goal}} | {{metric}} | {{target}} | {{owner}} | {{status}} |

## 3. Master Feature Inventory

Each product feature maps to its **owning repo** and the **CR/RFC/PRD artefact** that lands
it - reviewed in the `review` cadence. Do not restate the feature spec; link to it.

| PF ID | Feature | Owning repo | Child CR/RFC/PRD artefact | Priority | Status | Target release |
| --- | --- | --- | --- | --- | --- | --- |
| {{pf_id}} | {{feature}} | {{repo}} | {{repo}}:{{prd_feature_id}} | {{priority}} | {{status}} | {{release}} |

## 4. Cross-Repo Dependencies

| Dep ID | From repo | To repo | Dependency | Type | Required by | Status |
| --- | --- | --- | --- | --- | --- | --- |
| {{dep_id}} | {{from_repo}} | {{to_repo}} | {{dependency}} | api / data / event | {{date}} | {{status}} |

## 5. API Contract Commitments

The inter-repo seam where multi-repo products break. Version every contract; declare
breaking changes and a migration deadline.

| Contract | Owner repo | Consumers | Current version | Planned | Breaking change | Migration deadline | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {{contract}} | {{owner_repo}} | {{consumers}} | {{current}} | {{planned}} | {{breaking}} | {{deadline}} | {{status}} |

## 6. Risk & Conflict Register

| ID | Risk / conflict | Severity | Impact | Mitigation | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| {{risk_id}} | {{risk}} | {{severity}} | {{impact}} | {{mitigation}} | {{owner}} | {{status}} |

## 7. Decisions Log

| Date | Decision | Owner | Rationale | Related |
| --- | --- | --- | --- | --- |
| {{date}} | {{decision}} | {{owner}} | {{rationale}} | {{artifact_link}} |

---

<!-- Opt-in: only for large, multi-team products. Delete if not needed (keep the PVD lean). -->

## 8. PVD Topology (opt-in)

The master/domain/team PVD tree, for products large enough to need sub-PVDs.

| PVD ID | Name | Type | Owner team | Parent | Children | Sync status |
| --- | --- | --- | --- | --- | --- | --- |
| {{pvd_id}} | {{pvd_name}} | master / domain / team | {{team}} | {{parent}} | {{children}} | {{sync_status}} |

## 9. Governance Stage-Gates (opt-in)

| Gate | Name | Entry criteria | Evidence | Decision owner | Status |
| --- | --- | --- | --- | --- | --- |
| G1 | Epic approval | {{criteria}} | {{evidence}} | {{owner}} | {{status}} |
| G2 | Story approval (cross-team) | {{criteria}} | {{evidence}} | {{owner}} | {{status}} |
| G3 | Implementation review | {{criteria}} | {{evidence}} | {{owner}} | {{status}} |
| G4 | Integration validation | {{criteria}} | {{evidence}} | {{owner}} | {{status}} |
| G5 | Release approval | {{criteria}} | {{evidence}} | {{owner}} | {{status}} |

## 10. Release Coordination (opt-in)

**Window:** {{release_window}} · **Participating repos:** {{participating_repos}}

| Date | Milestone | Owner | Status |
| --- | --- | --- | --- |
| {{date}} | {{milestone}} | {{owner}} | {{status}} |

**Rollback / contingency:** {{rollback_plan}}

## Revision History

| Date | Version | Change | Author |
| --- | --- | --- | --- |
| {{date}} | {{version}} | {{change}} | {{author}} |
