# CR-0098: plan and audit flag Ready units whose verifiers already pass as already-satisfied

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**Estimate: 2 points. Folded in from a planning-run learning (LL0007).** The tranche audit
checks *mechanical* readiness (weak-AC, unmet-deps, terminal, links) but not whether a unit is
**already delivered** - a dogfooded plan queued 5 Ready stories whose features had shipped under
CRs. The deterministic signal was sitting there: **their verifiers all pass.** Add an
"already-satisfied" flag: a Ready unit whose executable ACs all pass (per the latest
verify-report, or a fresh `verify_ac` run) is surfaced as a **close-candidate**, not queued to
build. Advisory - the operator confirms (the feature may legitimately want a fresh story).

## Acceptance Criteria

- [ ] `audit check` (and `sprint plan`) flag a Ready unit whose executable ACs are all `yes`
      in `verify-report.json` as `already-satisfied` (a close-candidate), distinct from ready
- [ ] manual-only / AC-less units are not flagged (nothing executable to confirm)
- [ ] the flag is advisory (reported, never auto-closes); remediation names the likely action
      (verify + transition to Done, or close superseded)
- [ ] reuses the verify-report (no new verification path); unit test: an all-green Ready story
      is flagged, a partially-verified one is not; CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
