# US0034: product reconcile - cross-repo feature-map traceability

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0049)
> **Reviewer:** --
> **Created:** 2026-06-21
> **GitHub Issue:** --

## User Story

**As a** multi-repo product team
**I want** the PVD feature map verified against the child repos' PRDs
**So that** a product feature that does not trace to a real PRD feature is caught (RFC0015 WS3).

## Acceptance Criteria

### AC1: orphan + unknown-repo + missing-path block; in-sync passes

- **Given** a PVD feature map + a manifest + child PRDs
- **When** `product_reconcile` runs
- **Then** a feature not declared in its child PRD (orphan), a ref to an unknown repo, and a manifest repo with no path each block; a fully-traced map passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_product_reconcile.py::ProductReconcileTests::test_in_sync
- **Verified:** yes (2026-06-21)

### AC2: no false pass - declaration-anchored, never reads the wrong PRD

- **Given** a feature id mentioned only in prose, a substring-id collision, or a manifest repo missing its path
- **When** reconcile runs
- **Then** none yields a false in-sync (prose mention -> orphan; F7 != F70; missing-path -> blocking, not a fallback read of the manifest dir)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_product_reconcile.py::ProductReconcileTests::test_prose_mention_does_not_count
- **Verified:** yes (2026-06-21)

### AC3: degrades on absent repos with a visible un-verified count; exit codes

- **Given** an absent child repo or an empty feature map
- **When** reconcile runs
- **Then** it degrades (advisory) with an un-verified count, and `main` exits non-zero only on a blocking finding
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_product_reconcile.py::ProductReconcileTests::test_exit_codes
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/product_reconcile.py` (parse_feature_map, declaration-anchored prd_has_feature,
product_reconcile with orphan/unknown-repo/missing-path blocking + repo-absent/empty
advisory + un-verified count); reference-scripts.md entry. Manifest read via pvd.read_manifest.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0049) | Decomposed from CR0049 (RFC0015 WS3); critic REJECT->fixed (2 HIGH false-pass: missing-path fallback, free-text feature match) |
