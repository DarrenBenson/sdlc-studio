# CR-0128: test-strategy heuristics: production-state integration tests, regression-per-bug, contract rejects-old-shape

> **Status:** Complete
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

- [x] a new `best-practices/testing.md` captures the five heuristics with the one-line trigger for
      each ("when X, write test Y"); referenced from the test-spec workflow (`reference-test-spec.md`
      See Also + `best-practices/README.md`)
- [x] the test-spec template carries AC stubs for the applicable heuristics (production-state
      integration test, rejects-old-shape contract test, regression-per-bug) in a new "Strategy
      Heuristics" block so a generated spec surfaces them rather than relying on recall
- [x] **deterministic where possible** ([[LL0008]]): `audit` raises `missing-regression-test` for a
      bug at a terminal status (Fixed/Verified/Closed/...) whose recorded tests carry no
      integration/regression-level case (5 unit tests). See the advisory boundary below
- [x] cross-links: [[LL0005]] (review set includes a code leg) and [[LL0009]] (silent misleading
      failure - the bug class these integration tests catch) - in `best-practices/testing.md`
- [x] CHANGELOG `[Unreleased]` entry ([[LL0004]]); `npm test` + link checker green

## Delivery Notes: the advisory boundary

The checker mechanises a **name-level signal only**: it confirms a test of
integration/regression level is *named* on a terminal bug (a `Verify` line or a
`regression`/`integration`/`e2e` marker), and flags the bug when none is. It deliberately does
**not** attempt to prove a named test truly exercises the seams - whether a test is genuinely an
integration test rather than a unit test in an integration-named file is a judgement that stays
with the review code leg ([[LL0005]]). Heuristics 1 (production-state shape) and 3
(rejects-old-shape) are surfaced as test-spec AC stubs (a prompt, not a gate); heuristics 4
(resource-count) and 5 (extract-pure) stay advisory in `best-practices/testing.md`. This split is
the honest reach of mechanisation here: enforce the presence signal, leave the substance to review.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
| 2026-06-27 | Dani | Delivered: testing.md, template AC stubs, audit `missing-regression-test` checker + tests |
