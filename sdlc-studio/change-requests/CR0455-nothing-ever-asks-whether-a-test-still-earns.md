# CR-0455: Nothing ever asks whether a test still earns its place, so the suite only grows

> **Status:** In Progress
> **Decomposed-into:** EP0177
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/tests, tools/tests, .claude/skills/sdlc-studio/reference-test-best-practices.md
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK); agent; skill v5.0.0

## Summary

The repository carries 4,624 tests in 121 files against 70 source modules, and no process has ever reviewed whether any of them is still needed. Tests are added by every unit and removed by nothing. Because the full suite runs on every commit, each added test is a permanent tax on every future change, paid about 52 times in a single working day. `test_sprint.py` alone holds 429 tests that run whenever any script changes.

## Impact

Who: this project first, and any consuming project that follows the same discipline. What breaks: cost grows monotonically with no counter-pressure, and the growth is invisible because no report attributes suite time to the tests causing it. A suite nobody prunes eventually makes the discipline more expensive than the sloppiness it replaces, which is the adoption argument against the product.

## Acceptance Criteria

- [ ] A report attributes suite time and test count to the module each test covers, so the expensive areas are visible rather than guessed.
- [ ] A recurring review asks of each area whether its tests still discriminate - a test that no mutation of its own module can kill is a candidate for removal, not just a slow one.
- [ ] Removing a test requires the same evidence as adding one: a statement of what it no longer protects, recorded, so pruning cannot quietly become coverage loss.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK) | Raised |
