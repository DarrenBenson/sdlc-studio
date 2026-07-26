# RV-0017: CR0421 delivery closing review - EP0162 four units, one adversarial wave, APPROVE (MINOR-2 fixed, three declined)

> **Date:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

EP0162 / CR0421, four units US0433-US0436, diff `ac28cbd2..e0529b51`. One independent adversarial
wave by a fresh-context delegated reviewer (RFC0051/D0059) that did not author the code, recorded in
`sprint-review-record.md`. Probed: gate-weakening (batch-scoped conformance hiding an in-batch or
repo-global failure; the record-based currency path passing a genuinely-stale review), test vacuity
(value vs label; mutants), regressions from the `batch_changes` FIELDS/`_blank` seeding and the
conformance `scope_ids` rename, and the review-currency invariant.

## Findings

- No MAJOR. The four fixes do what their ACs claim; conformance scoping keeps in-batch and repo-global
  strength at full (verified by the exact count-delta test), and `--release` still judges everything.
- **MINOR-2 (fixed, e0529b51):** the growing-set trend offered `--file-and-close` unconditionally, but
  that exit refuses hard `gate` blockers - the exact kind a moving-target close produces - so it
  dangled a dead-end. Now the offer names file-and-close for the deferrable items only and says the
  hard lanes must be cleared.
- **MINOR-1 (declined):** record-based currency is an honesty gate - a hand-written future-dated
  `.local/review-state.json` passes the lane. Matches the trust model CR0421 requested; the file is
  gitignored/per-machine and already trusted by `review_prep.staleness`. Escalation is out of scope.
- **MINOR-3 (declined):** US0436 AC2's "the two checkers agree" holds only in the safe direction (the
  lane is more lenient, never more strict). The specific opposite-verdict bug the CR named is fixed.
- **NIT (declined):** `add_to_batch` normalises the whole batch while `drop_from_batch` preserves
  survivors verbatim - cosmetic, both feed `norm_id` readers.

Test quality confirmed by mutation, not inspection: the reviewer killed the US0436 hybrid and the
US0435 offer mutants; the author killed a further six guard mutants across the four units.

## Verdict

**APPROVE.** No MAJOR survives; the one substantive MINOR is fixed and the three residual findings are
declined with reasons recorded in RETRO0074. Reviewer-of-record sign-off (the operator) is OWED - the
two-role gate holds Done until it lands (units past `review.two_role_after` 192).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
