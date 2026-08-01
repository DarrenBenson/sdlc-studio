# CR-0520: a criterion verified only through the library is not evidence the feature ships

> **Status:** In Progress
> **Decomposed-into:** EP0199
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/best-practices/testing.md
> **Date:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

US0577 shipped `brief_fingerprint` with a passing acceptance test and a feature that did not work. The test computed `brief_fingerprint(critic.brief(...))` IN-PROCESS; the CLI command that issues a brief never called it, so nothing a reviewer could run produced the value the gate demanded. The changelog and the commit message both asserted the CLI emitted it. Green test, false claim, feature absent.

The same shape recurs. A library test cannot see a missing LANE: the wiring between the entry point and the function is exactly the part it does not exercise, and it is where this class of defect lives. Three of the five findings at the EP0194 boundary were of this kind - the feature was reachable from Python and not from the command.

This is mechanically detectable. When a unit's `Affects` names a script that exposes a CLI (an `argparse` parser, a `main()`, a `cmd_*` function), and the unit's own acceptance criteria are verified only by tests that import the module and call functions on it, nothing has demonstrated the command works. That is a discriminating signal, not a style preference.

## Impact

This is the defect class that costs review rounds rather than being caught by them, and it is the one an author is least able to see: the test passes, so the feature FEELS delivered. It cost two review rounds in RUN-01KYY52D alone, and the operator's standing objection is precisely that a change should need ONE review. Every round spent rediscovering that a lane was never wired is a round not spent finding something a reviewer is uniquely placed to find.

The author-side fix is a habit and will not hold - the whole premise of this repo is that a rule which is not gated is one that gets skipped (LL0027).

## Acceptance Criteria

- [ ] `verify_ac.py lane-check` reports criteria whose verifiers never enter the shipped entry point, for units whose Affects names a CLI-bearing script.
- [ ] A unit whose criteria ARE verified through the CLI is reported clean - the check must discriminate, not flag everything.
- [ ] Detection is by execution over the verifier's own test source (does it call main() or invoke the script), not by naming convention.
- [ ] The pass runs in the gate that already runs `verify_ac`, reporting only, with its yield accumulated where a later blocking decision can read it.
- [ ] A test pins the detector against the real US0577 shape: an in-process library verifier over a feature whose CLI never called the function - the mutant is a detector that returns clean on it.
- [ ] best-practices/testing.md states the rule beside 'name the mutant first': name the ENTRY POINT the test enters through, before writing it.

## Recommendation

Add a `verify_ac.py lane-check` pass, wired into the same gate that already runs `verify_ac`: for each unit whose Affects names a CLI-bearing script, report criteria whose verifiers never reach the entry point (no `main([...])` call, no subprocess invocation of the script). Report first while its yield is measured, exactly as claim-drift ships advisory, then decide on blocking from the number rather than from assertion.

Separately, `best-practices/testing.md` should name this beside 'name the mutant first': state the ENTRY POINT the test enters through before writing it, and if that is a Python import while the feature is a command, the test is not evidence for the claim being made.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Raised |
