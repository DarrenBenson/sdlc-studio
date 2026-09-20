# CR-0575: Low-severity crs (consolidated)

> **Status:** Rejected
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

## Why this was retired

**RETIRED 2026-09-20 (operator ruling).** This was a CONSOLIDATION artefact - a holding pen for the low-severity CR findings - not a change request. It could not be refined as written: `refine` decomposes a request into sized units, and there is no coherent decomposition of a bucket whose only shared property is a severity band. Left Proposed it sat permanently at the bottom of the discovery backlog, counted as an option awaiting refinement that nobody could ever take.

**Nothing is lost.** The underlying findings keep their own artefacts and their own severities, and `docs/known-issues.md` is GENERATED from the bug corpus rather than maintained by hand - so every one of them stays disclosed whether this page exists or not. Retiring the pen removes a number that was never actionable, not the work it pointed at. If a low-severity sweep is ever wanted, it should be filed as a request with a scope somebody chose, rather than inherited from a filter.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Consolidation opened |
| 2026-09-20 | operator ruling | Retired as Rejected. A consolidation bucket is not a change request and cannot be refined; the findings it pointed at remain, disclosed from the corpus. |
