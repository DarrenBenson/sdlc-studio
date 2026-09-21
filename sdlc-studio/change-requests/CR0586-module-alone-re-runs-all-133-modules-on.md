# CR-0586: module-alone re-runs all 133 modules on every push, 551 s of a 749 s gate, for a signal that changes only when a module's imports do

> **Status:** Proposed
> **Decomposed-into:** EP0253
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .githooks/pre-push, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Measured in RUN-01M2JA6J, 2026-09-16. corpus-verify on Lint run 35072360410: job 85.6 min, of which the red-criteria pass is 84 min and the dead-stamps pass 73 s, against a 90-minute job cap (raised to 150 in that run's repair). Run 35063993893 measured 75.9 min for the same pass. The pre-push boundary gate measured 749 s, of which module-alone is 551 s. Selector census over every story and bug: 3,439 Verify lines - 2,491 pytest node selectors, 386 WHOLE-MODULE pytest selectors, 366 shell, 126 grep, 58 manual.
> **Date:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The module-alone lane runs every skill test module alone under the unittest runner, one fresh interpreter each, and it costs 551 s of the 749 s push gate - 74% of the wall clock a push pays. Its yield is real and its shape is unarguable: `test_critic` was red alone for a month because a sibling imported a name first, and only this lane sees that. But the property it detects changes when a module's own imports or a shared helper move, not on every push, and a developer pays the full sweep to learn nothing on a push that touched one file. The lane is also the reason the boundary gate is 676% over its recorded baseline, which is the number that makes people reach for --no-verify.

## Impact

Every push, and therefore every close: an author who pays twelve minutes for a one-file change learns to batch pushes, which is how a red main survives six commits.

## Acceptance Criteria

- [ ] The push boundary runs the changed modules and their importers, and the lane's line names the selection and the rule that produced it
- [ ] The full sweep still runs on the schedule, and a week with no scheduled run is reported rather than silently skipped
- [ ] A module that the selection omits and the full sweep later finds red is recorded as a miss, so the rule's cost is measurable rather than asserted
- [ ] The push gate's measured wall clock is recorded before and after, beside `gate_timing`'s estimate

## Recommendation

At the push boundary run the modules whose files the push touches, plus every module importing a changed module, and keep the full 133-module sweep on the weekly schedule beside corpus-verify. Name the selection in the lane's line - which modules ran and why - so a narrowed lane is never mistaken for a full one, and record the selection's yield against the full sweep's so the narrowing is judged on evidence rather than on the wall clock it saved.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Raised |
| 2026-09-21 | audit ruling | still wanted, never started - returned to Proposed, and the gate is WORSE than it says. `_module_alone` still globs every test module (133 at HEAD) with no changed-module selection and no scheduled sweep to fall back on. The quoted 749s push gate has risen to 968s. Its own 551s share cannot be confirmed, because no per-lane series is recorded - which is exactly what its own US0843 asks for, so its AC4 currently has no instrument. |
