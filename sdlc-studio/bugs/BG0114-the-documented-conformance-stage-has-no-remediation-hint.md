# BG0114: the documented conformance stage has no remediation hint, and the guard meant to catch that is blind to it

> **Status:** Fixed
> **Verification depth:** functional
> **Target:** v4.1
> **Severity:** Medium
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering CR0235 (2026-07-13). The guard blind spot is a CLASS, not a single-stage miss: `test_registry_covers_every_emitted_finding_kind` fed itself a hardcoded `expected` set for every check, so it certified only the gaps it had been handed the answer key for. Confirmed across three checks:

- **conformance** - the `documented` stage can appear in a unit's `missing` list but had NO entry in the REMEDIATION registry, and the guard's hardcoded set ALSO omitted it.
- **reconcile** - emits EIGHT drift kinds; both the registry and the guard's set listed only FIVE. The three omitted (`breakdown-ticked-early`, `breakdown-unticked`, `index-status-column`) flowed through `by_kind` into `remediation_lines("reconcile", ...)` and produced empty guidance - and `breakdown-ticked-early` is the direction that masks unfinished work, so the operator got nothing for the most dangerous one.
- **audit** - emits eleven readiness issue kinds; the registry and the guard's set carried only seven. The four omitted (`weak-verify`, `missing-regression-test`, `cross-epic-ac`, `already-satisfied`) reached `remediation_lines("audit", ...)` and produced empty guidance.

This is the LL0008 false-assurance class (a check that reports success it did not achieve) driven by the LL0013 pattern (a guard that enumerates the kinds it checks silently exempts the kind it forgot).

## Steps to Reproduce

1. Read `test_registry_covers_every_emitted_finding_kind` - its `expected` sets were hardcoded per check. 2. For conformance, reconcile and audit, the hardcoded set matched the registry, so a kind missing from BOTH could not redden the guard. 3. `remediation_lines(check, {missing_kind})` returned `[]` for each omitted kind - the operator gets no guidance.

## Acceptance Criteria

- Every check whose finding kinds can drift from its registry exposes its real emission vocabulary as a single source of truth (`conformance.STAGES`, `reconcile.DRIFT_KINDS`, `audit.FINDING_KINDS`).
- The guard derives each such check's `expected` set from that vocabulary, not a hardcoded restatement, so a kind the check can emit but the registry lacks a hint for reddens the guard.
- A sibling test ties each vocabulary tuple to the kinds actually emitted in that module's source, so the tuple itself cannot silently drift.
- Every omitted kind above has an accurate, runnable remediation hint.

## Proposed Fix

Apply one derivation to each affected check: expose the emission vocabulary as a module constant, derive the guard's expected set from it, add a source-emission cross-check so the constant cannot drift, and add the missing hints. A guard that is handed its own answer key is not a guard. integrity has only two fixed kinds and no such drift surface, so it stays explicit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Filed |
| 2026-07-13 | Dani Okafor | Scope widened after independent-critic review: the blind spot is a class across conformance, reconcile and audit (not conformance alone). Amended the AC and Proposed Fix in place rather than filing a new bug (L-0001). |
