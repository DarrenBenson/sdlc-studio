# BG0237: Two dev-repo-only gate tests lack the skip guard, so the shipped suite fails from an installed copy

> **Status:** Fixed
> **Verification depth:** functional - the installed-copy condition was reproduced through the mechanism that causes it (`two_backlog_enforced` False at the expected root), giving the filed symptoms verbatim: `0 != 1` and `'awaiting another gate' not found`. Both fixes were then mutation-proven, and one mutant SURVIVED first time and drove a second fix.
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

tests/`test_gate.py` GateRealWrapperTests resolves REPO as parents[5], which is the dev repo root only when the skill tree sits inside this repo. From an installed copy (~/.claude/skills/sdlc-studio) it resolves to the home directory, which has no sdlc-studio/ workspace, so `sdlc_md.two_backlog_enforced` returns False, `gate._reconcile` skips the derivable-request sweep, and both tests fail on a count of 0. Three sibling tests in the same file already carry an explicit dev-repo-only skipTest guard (lines 119, 150, 257), so the class was recognised and the guard applied inconsistently. A consumer who runs the shipped suite from their install sees 2 failures out of 3409 with no indication the cause is location, not code.

## Steps to Reproduce

1. Forward-port the skill tree to an installed copy. 2. cd into the installed scripts/ dir. 3. python3 -m unittest discover -s tests. 4. Observe FAILED (failures=2): `test_gate_counts_a_derivable_request_that_apply_can_clear` (0 != 1) and `test_gate_does_not_block_on_a_request_another_gate_refuses` (detail missing 'awaiting another gate'). The same suite is 3409 OK from the dev repo.

## Proposed Fix

Add the same dev-repo-only skipTest guard the three sibling tests use, keyed on the sdlc-studio/ workspace being present under REPO. Prefer a shared helper or setUpClass guard on GateRealWrapperTests over a fourth hand-copied guard, so the next real-wrapper test inherits it rather than repeating the omission.

## Resolution

Fixed differently from the filed proposal, which asked for the same skip guard the three sibling
tests use. Skipping is the wrong remedy here: both tests already stub `detect_type` and
`derivable_request_drift` and were trying to be hermetic, they simply missed the third live
dependency. Stubbing `two_backlog_enforced` makes them location-independent, so an installed copy
gains the coverage a skip would have removed. Whether the detector is consulted at all stays
pinned, both ways, by the paired sibling test that was already there.

The bug also asked that the next real-wrapper test inherit the guard rather than repeat the
omission. Two changes deliver that:

1. The dev-repo guard moved INTO `GateRealWrapperTests._report()`, the single place that reaches
   the real gate, and the two hand-copied call-site guards were deleted. The rule now has one
   home instead of four copies that drift, which is the underlying complaint.
2. `test_no_test_in_this_class_fails_from_an_installed_copy` runs every other test in the class
   under the installed-copy condition and demands each PASS or SKIP. A future test that reads
   live state is caught however it is spelled, and the failure names it and states the remedy.

The `_report()` guard needed its own direct test. Deleting it was a SURVIVING mutant while both
callers guarded at their own call site: they skipped before reaching it, so it read as coverage
while being pinned by nothing (L-0159). Removing the redundant call-site copies made it reachable,
and `test_the_real_run_helper_refuses_from_an_installed_copy` now exercises it.

Verified the sweep does not consume the one allowed real gate run: the once-per-class assertion
still passes, so this did not recreate the restore-a-global regression of L-0176.

Module: 206 tests, green, 8.0s.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: hermetic stubs over a fourth skip guard; guard single-sourced into `_report()`; class-wide installed-copy sweep added. Mutant A (revert the stub) killed by the sweep, which named the test. Mutant B (delete the `_report()` guard) SURVIVED the first attempt, exposing an unreachable guard; after single-sourcing plus a direct test it is killed by 4 tests. |
