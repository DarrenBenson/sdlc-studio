# BG0237: Two dev-repo-only gate tests lack the skip guard, so the shipped suite fails from an installed copy

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
