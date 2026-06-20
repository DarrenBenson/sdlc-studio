# CR-0023: Complete the conformance gate - reconciled, reviewed, and a recorded critic verdict

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (determinism-sprint retro)
> **Date:** 2026-06-20
> **Affects:** scripts/conformance.py, scripts/ledger.py (or a critic-verdict record), reference-autosprint.md, RFC0001
> **Depends on:** RFC0001 (D3, WS7)
> **GitHub Issue:** --

## Summary

`conformance.py` checks `decomposed -> specified -> verifiable -> verified` and its
own docstring admits the `reconciled` and `reviewed` stages are "layered in later".
So a unit reported **conformant** is not actually known to be reconcile-clean or
reviewed, and the independent critic - which caught real defects in 3 of 5 built
units this sprint - leaves no committed trace and is never gated. "16/16 conformant"
overstates assurance: it is a partial oracle treated as complete, the exact
spec-gaming failure mode RFC0001 warns against. Finish the gate.

## Problem

- The conformance check does not verify a unit's epic/story is reconcile-clean.
- It does not verify the unit was reviewed.
- Nothing records that the independent critic (RFC0001 D3) ran or its verdict, and
  nothing hard-fails a unit that reached Done with the critic skipped.

## Proposed Changes

### Item 1: Verify the reconciled stage

**Priority:** High **Effort:** Low

For a Done unit, conformance confirms no `reconcile detect` drift for that unit's
story/epic (reuse `reconcile.py detect`).

### Item 2: Verify the reviewed stage

**Priority:** Medium **Effort:** Low

Confirm the unit appears in a review/closing-gate signal (review-state or the
closing reconcile+review record), so `reviewed` is asserted, not assumed.

### Item 3: A committed critic verdict, checked by conformance

**Priority:** High **Effort:** Medium

Record each unit's independent-critic verdict as a committed artifact (unit,
verdict APPROVE/REJECT, reviewer, issues, date - appended to the decisions ledger
or a `critic-verdicts` log). Conformance **hard-fails** a Done unit with no recorded
verdict, or with an unresolved REJECT. This makes "the critic ran" a deterministic,
auditable signal - the cheap 80% of RFC0001's deferred Stop-Hook (Option C), with
no harness dependency.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/conformance.py | Add reconciled + reviewed + critiqued stages | Modified |
| scripts/ledger.py (or new critic-verdict log) | Persist per-unit critic verdicts | New / Modified |
| reference-autosprint.md | The critic step writes a recorded verdict | Modified |
| RFC0001 | D3 critic becomes a recorded, gated signal | Referenced |

### Breaking Changes

Existing Done stories predate the critic record; gate the new `critiqued` stage on
units delivered after this CR (or backfill) to avoid retroactively failing history.

## Acceptance Criteria

- [x] A Done unit with `reconcile detect` drift on its story/epic is reported non-conformant.
- [x] A Done unit with no recorded critic verdict is non-conformant (conformance hard-fails).
- [x] A unit whose recorded critic verdict is an unresolved REJECT is non-conformant.
- [x] The critic verdict is a committed record (unit, verdict, reviewer, issues, date); reading it back is deterministic. Unit-tested.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (tooling-honesty-sprint) | Complete - US0017: critic.py committed verdict + conformance reconciled/critiqued stages; critic REJECT-then-fix broadened reconciled to missing-row |
| 2026-06-20 | Autosprint (determinism-sprint retro) | Raised - conformance stubs reconciled/reviewed and never checks the critic; "16/16" overstates assurance |
