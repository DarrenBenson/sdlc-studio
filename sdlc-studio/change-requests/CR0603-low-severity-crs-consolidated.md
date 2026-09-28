# CR-0603: Low-severity crs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-09-28
> **Consolidation:** low-severity-crs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **The report marks a known-issue ruling made by the unit's own author**: In eval 09 the author ruled its own filed bug not-stop-ship in the retro's carried table, and nothing drew the operator's eye to it: sign prints only stop-ship rulings. The ruled-by column is on the page but an author ruling on its own defect reads the same as an independent ruling.
- **A decision can supersede one ruling of an earlier multi-ruling decision**: `decisions.py add --supersedes D0279` marks the whole of D0279 superseded; its untouched rulings then read as void, so D0283 had to restate them. There is no clause-level supersession.
- **A filer can keep one Low finding out of the consolidation CR**: With `triage.low_consolidation: true` (this repository; off by default for consumers) every Low finding is folded into CR0592. Twice this sprint a Low the batch needed as its own unit had to be re-rated or folded to escape it; there is no per-filing opt-out.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Consolidation opened |
