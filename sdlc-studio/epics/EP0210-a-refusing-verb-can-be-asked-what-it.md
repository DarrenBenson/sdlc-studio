# EP0210: A refusing verb can be asked what it demands, before it refuses

> **Status:** Draft
> **Derived Point Total:** 24
> **Parent:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0535. Delivers the work CR0535 requested.

## Story Breakdown

- [ ] [US0646: A shared contract reporter derives a verb's demands by executing its own guard, never by restating them](../stories/US0646-a-shared-contract-reporter-derives-a-verb-s.md)
- [ ] [US0647: The vocabularies that gate a caller print from the constant that enforces them](../stories/US0647-the-vocabularies-that-gate-a-caller-print-from.md)
- [ ] [US0648: The four verbs whose refusals cost most in the measured session answer the contract reporter](../stories/US0648-the-four-verbs-whose-refusals-cost-most-in.md)
- [ ] [US0649: A lint lane counts contract-reporter coverage and names every refusing verb it cannot reach](../stories/US0649-a-lint-lane-counts-contract-reporter-coverage-and.md)
- [ ] [US0650: help and reference-scripts point at the contract reporter instead of restating any contract](../stories/US0650-help-and-reference-scripts-point-at-the-contract.md)
- [ ] [US0651: The refusals a run hits are counted, so the round-trip saving is a figure in the retro](../stories/US0651-the-refusals-a-run-hits-are-counted-so.md)

## Acceptance Criteria (Epic Level)

- [ ] A verb that can refuse can be ASKED what it will demand, before being run, and the answer is derived by executing its own guard rather than restated beside it - the pattern transition.py requirements already proves
- [ ] The input vocabularies that gate a caller - mutant edit verbs, DoR/DoD check ids, the Verify DSL verbs and their shell-prefix rule, option grammars, status vocabularies - are printable from the constant that enforces them, so a caller can read the accepted set without reading the source
- [ ] A lint lane asserts that every verb capable of refusing is reachable by the contract reporter, and names the ones that are not - coverage of 2 in 39 accumulated silently and will again without a lane that counts it
- [ ] help/ and reference-scripts.md POINT at the contract reporter rather than restating any contract, so no hand-maintained copy exists to drift
- [ ] The measured cost is reported: the number of refusals a run hits, so the claim that this reduces round-trips is a number in a retro rather than an assertion

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
