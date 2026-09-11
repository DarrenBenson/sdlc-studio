# BG0664: the pre-push boundary gate runs NO boundary-only test, so the marker's own promise is false at the boundary it names

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, .claude/skills/sdlc-studio/scripts/tests/boundary.py, tools/tests/test_pre_push_hook.py, tools/tests/test_boundary_marker.py
> **Evidence:** Push of 1a9f948d on 2026-09-10: `gate.py --boundary push` reported 23 lanes, all green, none of them a suite lane (conformance, reconcile, index-derived, validate, constitution, integrity, duplicate-id, provenance, doc-coverage, doc-surface, engagement-floor, disclosure, doc-freshness, mutation, window, hook-enabled, batch-size, changelog-fragments, derived-depth, evidence-drift, release-rehearsal, revert-check, module-alone). CI run 34539944618 on the same commit then failed on a `@boundary_only` test. `SDLC_STUDIO_BOUNDARY_SUITE` is exported at tools/run-suite.sh:192 and .github/workflows/lint.yml:65-80, and nowhere on the push path.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`boundary.py`'s docstring states that a marked test runs in FULL at every boundary, that `tools/run-suite.sh` sets the marker so every push, release, close and CI run executes it, and that it is deferred only in the per-commit selected run. Measured against what the push actually does, the first half is false. `.githooks/pre-push` runs `gate.py --boundary push`, and that gate runs NO test-suite lane at all: its 23 lanes are the artefact and doc checks plus release-rehearsal, revert-check and module-alone. `module-alone` does run every module, but under the plain unittest runner without `SDLC_STUDIO_BOUNDARY_SUITE`, so every `@boundary_only` test SKIPS there.

So a boundary-only test is executed by CI and by `tools/run-suite.sh`, and by nothing on the push path. The deferral `boundary_only` sells - `it reaches push before it reaches anyone else` - does not happen: it reaches main, and CI is the first thing to run it. Measured on the push of 1a9f948d, whose gate passed every lane while a boundary-only test was red on the very tree being pushed.

## Steps to Reproduce

1. Read the lane list of any `gate.py --boundary push` run: no suite lane appears.
2. `grep -rn SDLC_STUDIO_BOUNDARY_SUITE tools/ .github/` - it is exported by `tools/run-suite.sh` and by the CI workflow, and by nothing the pre-push hook invokes.
3. Mark any cheap test `@boundary_only`, make it fail, and push: the gate passes.
4. Measured instance: the push of 1a9f948d passed the boundary gate and CI then failed on `test_cli_grammar`'s boundary-only control (BG0663).

## Proposed Fix

Decide which is true and make the tree say it. Either the push boundary runs the full suite with the marker set - the reading `boundary.py` already publishes, at the cost of the suite's wall clock on every push - or the docstring is corrected to say that a marked test runs at CI and at `run-suite.sh` only, and the deferral is priced honestly. Whichever is chosen, a test must pin it, because this is a claim about which command runs which tests and nothing reads it today.

## Acceptance Criteria

- [ ] **AC1** Given the push boundary as the hook invokes it, when a `@boundary_only` test is red, then the push is REFUSED. Today it is not: the gate reports 23 green lanes and none of them executes a marked test, so the class the marker defers is a class the gate cannot see
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::BoundaryMarkerReachesThePushTests::test_a_red_boundary_only_test_refuses_the_push
- [ ] **AC2** Given `boundary.py`'s docstring, when it is read, then its claim about which runs execute a marked test matches what the push path does - checked by a test that reads the hook and the marker together, not by two documents agreeing with each other. The paired control: the claim must also stay true of the CI workflow, which does set the marker
  - **Verify:** pytest tools/tests/test_boundary_marker.py::MarkerPromiseTests::test_the_docstring_claim_matches_the_paths_that_set_the_marker
- [ ] **AC3** Given the per-commit gate, when it runs, then a `@boundary_only` test is still deferred there. A repair that runs every marked test everywhere removes the deferral rather than fixing the claim, and the marker exists because that cost was measured at 24% of the suite
  - **Verify:** pytest tools/tests/test_boundary_marker.py::MarkerPromiseTests::test_a_marked_test_is_still_deferred_in_the_per_commit_run

## Impact

The whole point of the pre-push gate is that a red main is prevented rather than discovered. A class of test exists that the gate cannot see, and its own documentation says otherwise - so an author reading `boundary_only` believes deferring a test costs nothing before the push, and it costs a red main. This repository's recorded failure mode is a rule stated in one place and not applied to the thing that exercises it; this is an instance in the gate itself.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
