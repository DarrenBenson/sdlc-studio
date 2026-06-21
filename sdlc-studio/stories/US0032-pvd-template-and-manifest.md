# US0032: PVD template + product manifest

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0047)
> **Reviewer:** --
> **Created:** 2026-06-21
> **GitHub Issue:** --

## User Story

**As a** team running a multi-repo product
**I want** a tiered Product Vision Document template and a child-repo manifest
**So that** the product layer above the PRD has a consistent, proportionate home (RFC0015 WS1).

## Acceptance Criteria

### AC1: Tiered PVD template (lean always, tree/gates opt-in)

- **Given** the PVD template
- **When** it is rendered
- **Then** the lean sections (vision, goals, feature inventory, cross-repo deps, contracts, risks, decisions) are present and the tree/gates/release sections are marked opt-in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd_template.py::PvdTemplateTests
- **Verified:** yes (2026-06-21)

### AC2: Feature map traces feature -> repo -> PRD feature; PM owns

- **Given** the template's feature inventory
- **When** read
- **Then** it maps a product feature to `<repo>:<prd-feature>` and names the Product Manager as owner (coordinate-not-respecify)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd_template.py::PvdTemplateTests::test_feature_map_traces_to_repo_and_prd_feature
- **Verified:** yes (2026-06-21)

### AC3: Manifest lists child repos (id / path / url)

- **Given** the product manifest template
- **When** read
- **Then** it carries product, master_pvd, and a repos list with id / path / url
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_pvd_template.py::ManifestTemplateTests
- **Verified:** yes (2026-06-21)

## Implementation

`templates/core/pvd.md` (tiered), `templates/product-manifest.yaml`, `reference-pvd.md`,
`help/pvd.md`, SKILL.md rows (Type Reference `pvd` + Progressive Loading). Template/doc
only - no executable logic; verified by the completeness test + lint (no logic-critic).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0047) | Decomposed from CR0047 (RFC0015 WS1); template+manifest+docs, completeness-tested |
