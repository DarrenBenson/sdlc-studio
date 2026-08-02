# BG0487: lane-check misses lane entry made through a shared test helper

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/US0605.md, changelog.d/BG0487.md
> **Verification depth:** functional (two mutants KILLED by exactly the intended test - helper resolution removed, and whole-file fallback restored; corpus re-measured over the same 615 units, 186 -> 167, with US0577's original library-not-lane defect still reported)
> **Severity:** Medium
> **Points:** 2

## Summary

lane-check scopes its search to the named test node, which was the fix that made the detector fire at all - whole-file matching reported 0/615. But a test class that shells the CLI once in a `_run`/`_invoke` helper and calls `self._run(...)` from every test method is a correct and common shape, and the scoped node then shows only the helper call. The detector reports it as never entering the lane.

Found by US0471's own front-door check: lane-check flagged US0471, whose tests call `sprint.main([...])` inside `self._run`. Two further units delivered this same sprint, US0609 and US0615, are flagged for exactly this reason. The detector is telling correctly-tested work it is untested, which is how a reported-only lane earns its way to being switched off before it ever earns the right to block.

## Steps to Reproduce

1. `verify_ac.py lane-check --ids US0471`
2. Read `test_batch_capacity.py::AddEpicTests` - every method calls `self._run`, which calls `sprint.main([...])`.
3. The finding says NONE of its 4 verifiers enters the shipped entry point.

## Proposed Fix

Resolve ONE level of same-file helper: from the scoped node, take the names called as `self.<name>(` or bare `<name>(`, and credit the node if any of those functions in the same file enters the lane. One level, not a call graph - deeper resolution reintroduces the whole-file permissiveness that made the first version report nothing. Re-measure the corpus yield afterwards and record the new number, since the recorded yield is what the blocking decision rests on.

## Impact

A detector shipped this sprint reports correctly-tested units as untested, including three of the sprint's own. It is advisory, so nothing is blocked, but the yield number it is being measured on is inflated by false positives - and the decision to let it block later rests on that number.

## Acceptance Criteria

### AC1: entry made through a shared test helper is credited

- **Then** a node that calls `self._run(...)`, where `_run` enters the shipped entry point,
  is not reported
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_entry_made_through_a_shared_test_helper_is_credited
- **Verified:** yes (2026-08-02)

### AC2: resolution is one level, and does not credit the whole file

- **Then** an unrelated helper elsewhere in the same file entering the lane does NOT clear a
  library-only verifier, so the permissiveness that reported 0/615 is not restored
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_helper_resolution_is_one_level_and_does_not_credit_the_whole_file
- **Verified:** yes (2026-08-02)

### AC3: the original defect shape is still reported after the fix

- **Then** a criterion whose verifier only calls a library function, in a class whose OTHER
  methods enter the lane, is still reported - the shape the repair could plausibly have hidden
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::LaneCheckTests::test_a_library_only_method_beside_lane_entering_ones_is_still_reported
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
