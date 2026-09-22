# CR-0592: Low-severity bugs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-09-21
> **Consolidation:** low-severity-bugs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **conformance hard-codes the Verified positive vocabulary that sdlc_md now owns, so the two will diverge the next time it changes**: BG0733 named the set of `Verified:` values that mean satisfied as `sdlc_md.VERIFIED_POSITIVE`, a frozenset of `yes` and `manual`. `conformance.py` carries the same pair as a literal tuple and compares against it independently. Two code paths now decide the same question from two definitions - LL0016 in the lessons registry is exactly this - and the next value added or removed will be added or removed in one of them.
- **the abandoned lens costs the triage sweep a quarter-second because every artefact is date-parsed, though only the children of In Progress requests are ever read**: BG0722's `abandoned` lens needs each artefact's last-touched date, so `_scan` now runs `_last_date` over all 2526 artefacts rather than the backlog subset. Measured by the reviewing seat, `triage()` went from 0.284s to 0.532s on this repository. Both `status` and `sprint plan` call it interactively. The `dates` map is only ever read for artefacts named as children by an In Progress cr/rfc - seven of them here - so almost all of that parse is discarded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Consolidation opened |
| 2026-09-21 | US0853 AC2 | The two BG0463 survivors this bucket had absorbed are minted as their own artefacts, BG0734 and BG0735, and removed from here. US0853's AC2 says nothing carries forward as a bullet inside another artefact, and delivery review was right that a bucket is exactly that. This page keeps whatever else it consolidates. |
