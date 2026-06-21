# CR-0049: product reconcile - cross-repo feature-map traceability (RFC0015 WS3)

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson (RFC decision session)
> **Date:** 2026-06-21
> **Affects:** scripts/product_reconcile.py (new)
> **Depends on:** RFC0015, CR0047, CR0048
> **GitHub Issue:** --

## Summary

Verify the PVD feature map across the child repos: every PVD master feature resolves to a real child PRD feature and vice-versa (orphans + unmapped flagged). Reads sibling repos via the manifest; degrades if a repo is absent.

## Proposed Changes

- `product reconcile` reads each child repo (manifest paths) and checks the feature map both ways.
- Reports orphan PVD features (no child feature) and unmapped child features; exits non-zero on drift.

## Acceptance Criteria

- [ ] Given a PVD + child PRDs, product reconcile reports 0 drift when the map is complete and flags orphans/unmapped otherwise.
- [ ] A missing/unreadable child repo degrades to a warning, never a crash.
- [ ] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
