# EP0199: A criterion verified only through the library is visible, so a feature cannot pass its own gate while its lane is unwired

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0520
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0520. Delivers the work CR0520 requested.

## Story Breakdown

- [x] [US0605: verify_ac lane-check reports criteria whose verifiers never enter the shipped entry point, for units whose Affects names a CLI-bearing script](../stories/US0605-verify-ac-lane-check-reports-criteria-whose-verifiers.md)
- [x] [US0606: The lane-check runs in the gate that already runs verify_ac, reporting only, with its yield accumulated where a blocking decision can read it](../stories/US0606-the-lane-check-runs-in-the-gate-that.md)
- [x] [US0607: best-practices/testing.md states the entry-point rule beside name-the-mutant-first](../stories/US0607-best-practices-testing-md-states-the-entry-point.md)

## Acceptance Criteria (Epic Level)

- [ ] `verify_ac.py lane-check` reports criteria whose verifiers never enter the shipped entry point, for units whose Affects names a CLI-bearing script.
- [ ] A unit whose criteria ARE verified through the CLI is reported clean - the check must discriminate, not flag everything.
- [ ] Detection is by execution over the verifier's own test source (does it call main() or invoke the script), not by naming convention.
- [ ] The pass runs in the gate that already runs `verify_ac`, reporting only, with its yield accumulated where a later blocking decision can read it.
- [ ] A test pins the detector against the real US0577 shape: an in-process library verifier over a feature whose CLI never called the function - the mutant is a detector that returns clean on it.
- [ ] best-practices/testing.md states the rule beside 'name the mutant first': name the ENTRY POINT the test enters through, before writing it.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
