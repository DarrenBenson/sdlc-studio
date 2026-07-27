# CR-0444: sprint plan validates the batch it is about to plan, not only its index rows

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, pre-sprint check discussion); agent; skill v5.0.0

## Summary

`sprint plan` already reconciles before planning - `_preplan_reconcile` runs so a plan reads a drift-free census - but its own docstring scopes it to 'mechanical drift only: file Status vs its index row'. `validate.py` is never invoked by sprint at all. So a batch can plan cleanly while every unit in it declares a footprint the workspace contradicts, which is exactly what happened on 2026-07-27: sixteen units planned into RUN-01KYHVWK, every one declaring a single source file and none its test file, while validate reported 191 affects-undeclared warnings nobody was reading.

The fix that works is scoping, not severity. A corpus-wide check cannot block, because 191 pre-existing instances would refuse every plan on day one; scoped to the batch it is a handful of units at the one moment an operator can still act on them, and it can legitimately gate. It also pays the backlog down lazily and in the right order - a unit nobody plans never needs fixing, and a unit about to be built is fixed before it is built.

## Impact

Who: every operator planning a sprint, and every consuming project, since the same advisory posture ships. What breaks: an understated footprint under-reads the unit in the engagement floor, mis-groups it in the plan's own collision analysis, and misreports it in gate's changed-surface pass - the three harms the repo's refine guard already names when it refuses a fictional footprint. The planner causes all three silently because nothing checks the batch. Concretely, BG0314, BG0315 and BG0316 all change transition.py and all needed `test_transition.py`; the test-file collision was invisible to the plan that grouped them.

## Acceptance Criteria

- [ ] sprint plan runs the structural validation scoped to the units it resolved for the batch, and names each unit whose Verify lines target a file its Affects omits, with the missing path.
- [ ] The scope is the batch and never the corpus, so pre-existing instances in units nobody is planning cannot refuse a plan whose own units are clean.
- [ ] The same check covers a unit added to an open run afterwards, so joining a batch late is not a way past it.
- [ ] Whether an offending unit blocks or warns is configurable, and the default is stated in the help rather than left to be discovered from the source.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (operator-raised, pre-sprint check discussion) | Raised |
