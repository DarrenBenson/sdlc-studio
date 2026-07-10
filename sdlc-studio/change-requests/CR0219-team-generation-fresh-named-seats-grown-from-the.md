# CR-0219: team generation: fresh named seats grown from the project (persona generate --team)

> **Status:** Proposed
> **Depends on:** CR0218
> **Priority:** High
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

RFC0028 core. Analyse PRD/TRD/TSD/config/repo-map onto behavioural variables and risk axes (never demographics); ask hard-capped multi-choice questions when signals are ambiguous (Lena: <=4 default, <=1 --quick; inferences defaulted-and-displayed with one batch adjust prompt); generate fresh named individuals per project on the amigo-template schema into seats/ - 3 core roles + up to 2 signal-proposed extras (Security/SRE/Data/UX), cast capped 3-5. Depends on the converged-home CR.

## Acceptance Criteria

- [ ] The --team flow follows Analyse -> Present discoveries -> Ask (<=4 default / <=1 quick, one at a time, every inference contestable via one batch adjust) -> Generate -> batch-accept close that clears TEAM provisional labels in-flow; headless runs keep the provisional stamp
- [ ] Generated seats: declared role comment, dual render, Craft Goals/Non-Negotiables/Pushes-Back-When/Shadow grounded in the analysed domain and stack; a role-claiming amigos/ card triggers the migrate/retire path, never silent shadowing
- [ ] A new error-level validate.py seats check owns the D4 hard error: role comment present and allowed, review-render headings present, provenance stamp present on generated cards, demographic-token denylist clean, seat cast 3-5 (Sam, blocking)
- [ ] Never-clobber: authored-vs-generated discriminated by provenance stamp PLUS content hash; re-runs key on declared role (one generated card per role, diffing its own prior); --dry-run first-class
- [ ] status emits an advisory count of unreviewed provisional seats; standalone repo-map-only invocation documented with a hint after review generate
- [ ] Eval scenario 07: fixture ambiguous by design (conflicting risk classes, absent compliance regime) with scripted answers and the expected question axis in `grading_notes`; EBs include ask-before-write ordering, authored-seat byte-identity across run and re-run, domain keyword floor, forbidden headless-dodge

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
