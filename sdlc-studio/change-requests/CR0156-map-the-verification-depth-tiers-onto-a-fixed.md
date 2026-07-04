# CR-0156: map the verification-depth tiers onto a Fixed to Verified bug progression (define the dormant Verified status)

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** reference-test-best-practices.md (verification-depth tiers), reference-outputs.md (status transitions), templates/core/bug.md, transition.py (the depth gate already exists)
> **Found by:** a consuming project executing a real bug sprint

## Summary

The verification-depth discipline (a Fixed transition is gated until the bug records a `functional`+
tier) routinely produces a state the bug vocabulary cannot express: **the fix is implemented and
verified at the functional tier, but the higher tier (e2e / live) that actually proves it is still
owed.** CRs solved the equivalent with a `Built` half-state; bugs have no counterpart.

Observed live: a governance-display fix was implemented and unit/component-verified (mutation-checked),
but its real proof is an e2e run against a deploy that could not run in the session. The available bug
statuses were only `Fixed` (overstates - the meaningful proof is owed, and for a render surface
unit-green is exactly the false assurance the tranche existed to kill) or `In Progress` (understates -
the code is done, not still being worked). Neither is honest.

There is an elegant fix already sitting in the vocabulary: **`Verified` is a valid bug status that is
never used** (in the consuming project: 123 `Fixed`, 3 `In Progress`, **0 `Verified`** across 126
bugs). Give it the obvious meaning and the half-state falls out for free.

## Proposed change

Define the two-tier terminal progression and map it onto the existing verification-depth tiers:

- **`Fixed`** = the fix is implemented and verified to the **functional** tier (unit / component /
  contract) - the tier `transition.py` already gates on. Terminal-enough to close a routine bug.
- **`Verified`** = the fix is additionally proven at the **higher tier its risk demands** -
  e2e / conversational / soak / live-with-real-data (per `reference-test-best-practices.md`
  verification-depth-tiers). This is the honest home for "code done + functional-verified, live proof
  landed".

So a render / navigable-surface / live-data bug is **`Fixed`** when implemented + unit-green, and
becomes **`Verified`** when the e2e/live run passes - instead of being forced into a dishonest `Fixed`
or a misleading `In Progress`. Document it in `reference-outputs.md` (status transitions) and
`reference-test-best-practices.md` (tie the tiers to the two statuses); no new status is invented -
`Verified` already exists, it just has no defined meaning today.

Optionally, `transition.py` can require the higher-tier evidence line for `Fixed -> Verified` the same
way it already requires `functional`+ for `-> Fixed` - the gate machinery exists.

## Acceptance Criteria

- [ ] `reference-outputs.md` documents the `Fixed` (functional) -> `Verified` (higher-tier) bug
      progression, tied to the verification-depth tiers in `reference-test-best-practices.md`.
- [ ] A bug fixed + functional-verified but with an e2e/live tier owed has an honest status
      (`Fixed`), and a promotion path (`Verified`) once the higher tier lands - neither `In Progress`
      nor a false full-proof `Fixed`.
- [ ] `transition.py` optionally gates `-> Verified` on a recorded higher-tier evidence line (reusing
      the existing depth-gate), with a unit test.

## Notes / provenance

Found running a 6-bug sprint in a consuming project: three fixes were code-complete + unit-verified but
e2e-gated against a deploy unreachable in the session, and no bug status expressed that half-state
(`Built` is CR-only). The `Verified` status was already in the project's vocab but had 0 uses. This is
the bug-side counterpart of the CR `Built` half-state, and it makes the verification-depth tiers
legible in the status itself rather than only in a prose `Verification depth` line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-project dogfooding) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-project dogfooding) | Filled in from sprint execution: the depth gate produces a code-done-but-live-owed state bugs can't express; define the dormant `Verified` status as the higher tier so `Fixed`->`Verified` maps onto the verification-depth tiers. |
