# BG1508: BG1506's tests catch only the unstamped writer's stale patch: pointing the at_close or at_sign patch back at the load-time module leaves its criteria green

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1508.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:24Z

## Summary

From BG1506's round-one QA review (APPROVE, non-blocking). (1) AC1's 'Fails on' over-claims: reverting the `at_sign` patch (`test_evidence_schema_stamp.py`:106) or the `at_close` patch (:89) to the module imported at load time leaves AC1 and AC2 green, and a `run_state.py` record-version mutant is caught by the committed test but not with `at_sign` reverted under a forced swap. (2) The comment at `test_sprint_report.py`:2507-2508 overstates the hazard ('a module nobody calls'): only code that re-imports `sprint_report` at call time (sprint.py's close and sign paths) misses the patch. (3) BG1506's Proposed Fix credits the stamp file's 'own docstring' with saying the close reads the live module; that is `_live`'s docstring in `test_evidence_annex_report.py.`

## Steps to Reproduce

1. In `test_evidence_schema_stamp.py`, point the `at_sign` patch (line 106) back at the module imported at load time.
2. Run the file and BG1506's AC1 and AC2 Verify lines: they stay green.

## Proposed Fix

Add a forced-swap case that fails when either `at_close` or `at_sign` patches the load-time module, narrow the comment to the call-time re-import, and correct the Proposed Fix's attribution.

## Acceptance Criteria

- [ ] **AC1** Given the stamp tests' `at_close` patch pointed at the `sprint_report` module imported at load time while a fresh module sits in sys.modules, when the forced-swap case runs, then it detects that the close read an unpatched module and fails. Fails on: a stale-module patch on the close step leaving every stamp criterion green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_a_close_patch_on_the_load_time_module_is_caught_under_a_forced_swap
- [ ] **AC2** Given the `at_sign` patch pointed at the load-time module under the same forced swap, when the forced-swap case runs, then it fails the same way, and with both patches on the live module it passes. Fails on: the sign step covered only by the unstamped writer's test, or a forced-swap case that fails whatever is patched.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py::EvidenceSchemaStampTests::test_a_sign_patch_on_the_load_time_module_is_caught_under_a_forced_swap

## Impact

A later edit can reintroduce the stale-module patch on the close or sign step without any criterion going red.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
