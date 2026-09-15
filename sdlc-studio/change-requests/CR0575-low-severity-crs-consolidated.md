# CR-0575: Low-severity crs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-09-15
> **Consolidation:** low-severity-crs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **A filed artefact carries no back-link to the unit and REJECT whose finding it discharges**: US0628 writes Findings-filed-to on the closing unit; the reverse link does not exist. `file_finding` stamps only Raised-in-batch, so a reader of the filed bug cannot find the review that raised it.
- **Findings-filed-to is invisible outside the unit file: undocumented, and status and the sprint report read a Done over a REJECT as clean**: The field US0628 introduces is not catalogued where metadata fields are documented, and status and the sprint report do not distinguish 'Done, findings filed to X' from a clean Done.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Consolidation opened |
