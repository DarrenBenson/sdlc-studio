# CR-0128: test-strategy heuristics: production-state integration tests, regression-per-bug, contract rejects-old-shape

> **Status:** Proposed
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/best-practices/testing.md
> **Depends on:** -

## Summary

Distilled from recurring test-strategy lessons in BOTH consuming projects (a consuming repo
EP0037-0039 + smoke-test findings; a second consuming repo v1.3.0-v1.6.0). The same five heuristics keep being
relearned, so they belong in the skill's best-practices and, where mechanisable, in the test-spec
ACs the skill generates:

1. **Production-state-shape integration tests.** Unit tests construct trivial state and miss
   correctness bugs that only manifest under non-trivial production shape: multi-turn history arrays,
   resolve-then-cancel races (a consuming repo BG0026/28/29 all escaped unit tests). For any path whose
   behaviour depends on production state shape, require at least one integration test that injects
   the non-trivial shape.
2. **A named regression test per production bug** at the integration level (router -> dispatcher ->
   channel loop), not a unit test on the root-cause file. Unit tests prove a piece works in
   isolation; the bug lived in the seams.
3. **Contract changes ship a `rejects_OLD_shape` test beside `parses_NEW_shape`.** a second consuming repo missed
   a bridge contract drift for weeks; one rejects-old-shape test would have caught it on first push.
4. **Resource-count regression tests for subscriptions** (listener-count baseline -> exercise full
   lifecycle -> assert baseline restored). A `.off` that does not match its `.on` leaks silently
   otherwise.
5. **Extract pure functions; test those.** IO-free logic embedded in an IO wrapper needs an
   order-of-magnitude more expensive fixture harness. Extract, type the in/out, unit-test the pure
   core, leave the wrapper thin.

These are generic quality heuristics, not project facts. To honour the determinism doctrine they
must not live only as advice an agent may forget: where a heuristic can be checked mechanically it
should be, and the test-spec template should carry the ACs so generated test specs prompt for them.

## Acceptance Criteria

- [ ] a new `best-practices/testing.md` captures the five heuristics with the one-line trigger for
      each ("when X, write test Y"); referenced from the test-spec workflow
- [ ] the test-spec template carries AC stubs for the applicable heuristics (production-state
      integration test, rejects-old-shape contract test) so a generated spec surfaces them rather
      than relying on recall
- [ ] **deterministic where possible** ([[LL0008]]): a checker (extending `tools/` or
      `scripts/verify_ac`) flags a bug marked Fixed/Done whose linked test set has no integration- or
      regression-level case, rather than leaving "regression-test-per-bug" as unenforced prose; if
      full mechanisation is infeasible the CR records exactly what stays advisory and why
- [ ] cross-links: [[LL0005]] (review set includes a code leg) and [[LL0009]] (silent misleading
      failure - the bug class these integration tests catch)
- [ ] CHANGELOG `[Unreleased]` entry ([[LL0004]]); `npm test` + link checker green

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
