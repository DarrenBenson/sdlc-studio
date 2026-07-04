# CR-0049: product reconcile - cross-repo feature-map traceability (RFC0015 WS3)

> **Retired 2026-07-04 (CR-0142).** This shipped `product_reconcile.py`, which dogfooding later
> showed never produced a true trace against a real PVD (parsed 0 of 11 features; its green tests
> pinned a synthetic token format reality never used). The tool is removed; feature-map integrity
> is now a `review`-cadence job and the working cross-repo tooling is `pvd sync` / `pvd drift`.
> The ship fact stands - it was Complete on 2026-06-21; it is now Superseded.
>
> **Status:** Superseded
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

- [x] Given a PVD + child PRDs, product reconcile reports 0 drift when the map is complete and flags orphans/unmapped otherwise.
- [x] A missing/unreadable child repo degrades to a warning, never a crash.
- [x] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0049) | Complete - US0034: product_reconcile.py; critic REJECT->fixed (2 HIGH false-pass) |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
