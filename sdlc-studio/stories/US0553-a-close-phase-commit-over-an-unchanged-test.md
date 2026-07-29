# US0553: A close-phase commit over an unchanged test-relevant surface reuses the gate verdict the close itself earned, rather than re-running the suites

> **Status:** Blocked
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-commit
> **Epic:** EP0189
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator closing a sprint
**I want** the close's own full gate run to record the verdict it earned
**So that** the commits that follow it over the same script tree reuse that verdict instead of re-running the whole suite each time

## Premise - FALSIFIED

This story was built on the belief that `sprint close` runs the FULL unit suites at step 4 of
seven, and therefore holds a green it may record for the commits that follow.

It does not. `_close_gate` invokes `gate.main`, whose lanes are conformance, reconcile, validate,
constitution, integrity, duplicate-id, provenance, doc-coverage, engagement-floor, disclosure,
doc-freshness, mutation, window, hook-enabled, batch-size, changelog-fragments and index-derived.
**Not one of them runs a test suite.** The suites are run by `.githooks/commit-msg`, which is the
only honest writer of `gate-suite-verdict.json`.

The delivered code therefore stamped `status=green, mode=full` over whatever sat in the working
tree, and the next commit read that record and ran no tests - a false green produced by the
mechanism built to refuse false greens. Reproduced end to end at the closing review: with a
deliberately failing test present, `suite_decision` reported `run=True`; after the call this story
added, it reported `run=False, mode=reuse, "running no tests"`.

REVERTED rather than repaired. There is no repair: the saving this story claimed does not exist,
because the cost it claimed to avoid was never paid at that point in the chain. The close's own
gate verdict is already reused correctly and close-scoped through `reusable_close_verdict`.

`test_sprint.py::CloseRecordsNoSuiteVerdictTests` guards the revert, and asserts the PREMISE
directly - if a gate lane ever genuinely runs the suites, that test says so and this decision can
be revisited on evidence rather than on belief.

## Acceptance Criteria

The story is REVERTED. These criteria assert the revert holds and the premise stays checked -
they are what a reader needs to know before anyone reinstates this.

### AC1: the close records no suite verdict

- **Given** a `sprint close` whose gate passes
- **When** the chain's gate step completes
- **Then** no suite verdict is written, because `gate.main` runs no test suite and any green it
  recorded there would be fabricated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRecordsNoSuiteVerdictTests::test_a_passing_close_writes_no_suite_verdict
- **Verified:** yes (2026-07-29)

### AC2: the falsified premise is itself checked

- **Given** the gate's lane registry
- **When** it is read
- **Then** no lane runs a test suite - so if one is ever added, this test says so and the revert
  can be revisited on evidence rather than on belief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRecordsNoSuiteVerdictTests::test_the_close_gate_runs_no_suite_lane
- **Verified:** yes (2026-07-29)

### AC3: the close-scoped verdict reuse is untouched

- **Given** two close attempts over an unchanged surface
- **When** the second runs
- **Then** it reuses the close's own gate verdict - that mechanism is correct and close-scoped,
  and reverting the fabricated SUITE verdict must not take it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRecordsNoSuiteVerdictTests::test_the_close_scoped_verdict_reuse_is_untouched
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
