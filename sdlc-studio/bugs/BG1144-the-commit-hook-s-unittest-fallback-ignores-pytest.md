# BG1144: The commit hook's unittest fallback ignores pytest's serial_only and boundary_only marks, so a push-only test still runs on a commit there

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/boundary.py, tools/tests/test_boundary_marker.py
> **Evidence:** BG0963 REJECT round 1 by qa-seat-BG0963-r1, [pre-existing] finding; sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T01:36:42Z

## Summary

qa-seat-BG0963-r1 (2026-11-01) found that .githooks/commit-msg:290-314 runs tools/skill-tests.sh under `python3 -m unittest` when pytest is absent, or when the handoff names no suite selector. `pytest.mark.serial_only` and `pytest.mark.boundary_only` do nothing under unittest, so a test marked to run only at push runs on that commit path. Example: `python3 -m unittest test_config.IntegrationTests.test_status_gathers_a_fixture_never_this_repository`, with no boundary environment, ran (OK, 2.2s) rather than skipping. This predates BG0963: the bounds ran unmarked on that path at the base ref too. The `boundary.boundary_only(reason)` skipUnless helper defers a test under both runners.

## Steps to Reproduce

1. Without the boundary environment, run `python3 -m unittest` on any test that carries only `@pytest.mark.boundary_only`.
2. Expected: skipped, as under pytest. Actual: it runs.

## Proposed Fix

Have every `boundary_only` test use `boundary.boundary_only(reason)`, or a decorator that applies both the pytest mark and the skipUnless, and add a census line that refuses the pytest mark alone. Or make the commit-msg fallback deselect marked tests.

## Acceptance Criteria

- [ ] **AC1** Under `python3 -m unittest` with no boundary environment, a `boundary_only` test is skipped, as it is under pytest.
  - **Verify:** pytest tools/tests/test_boundary_marker.py
- [ ] **AC2** A test carrying only the pytest `boundary_only` mark, without the both-runner form, is named by the boundary-marker census.
  - **Verify:** pytest tools/tests/test_boundary_marker.py

## Impact

On the fallback path a commit pays for the push-only tests and can be refused by a wall-clock bound under load, which BG0963 exists to stop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
