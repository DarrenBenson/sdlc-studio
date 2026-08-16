# BG0493: four more verifiers pass on a delivery that has been made inert

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/conftest.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/best_practice_rules.py, tools/tests/test_best_practice_rules.py, tools/tests/test_conftest_guard.py, tools/tests/test_precommit_lane_order.py
> **Severity:** Medium
> **Points:** 3

## Summary

The residue of the source-grep verifier class after 307ce91d repaired the blocking half. Each was demonstrated by an independent pass, by mutation.

BG0476 - replacing `sys.path.insert(0, ...)` with `pass` in tools/tests/conftest.py SURVIVES both ACs. AC1's `assertIn("sys.path.insert", conftest.read_text())` is satisfied by the file's own DOCSTRING at line 8. The Resolution's 'deleting conftest.py KILLS the guard' is true of AC1 only; AC2 stays green.

US0606 - AC1's `text.split("lane-check")[1][:600]` lands entirely inside a COMMENT block, so its `assertIn("|| true", block)` is satisfied by an unrelated pipeline. Dropping the lane's own `|| true` survives.

US0607 - `best_practice_rules.py` returns 0 when the practice file is ABSENT, so the exemption is reachable by deleting the file - the shape US0608 AC4 exists to prevent. It is also wired into no gate: no caller in .githooks/, package.json or tools/.

BG0423 - `Verification depth: functional`, but both verifiers are source-text greps over .githooks/commit-msg and nothing executes the hook.

## Triage 2026-08-15

Re-measured before any code was written. **Three of the four instances stand** and the fourth is narrowed out explicitly below, so this bug is
carried NARROWED - the opposite finding to BG0490 beside it, and the reason each was measured rather
than assumed from its age.

| Instance | Measured now |
| --- | --- |
| BG0476 | **STANDS** - `sys.path.insert` appears twice in `tools/tests/conftest.py`, at line 8 in the DOCSTRING and line 15 as the real call, so AC1's `assertIn` is satisfied with the call deleted |
| US0606 | **STANDS** - the `lane-check` slice still opens inside a comment block, and the `\|\| true` its assertion finds belongs to an unrelated pipeline |
| US0607 | **STANDS** - `best_practice_rules.py` is referenced by nothing in `.githooks/` or `package.json`, so it is wired into no gate |
| BG0423 | **NOT RE-MEASURED.** Named in the Summary as the fourth instance and carried by no criterion here. An independent review found it dropped while the section claimed the bug was carried unnarrowed - which is the exact fault BG0490 beside it was filed to record, committed in the artefact recording it. It is narrowed OUT explicitly rather than left ambiguous, and needs its own re-measurement before it is worked |

Not built here: each repair is a test-strengthening change to a guard, which is engineering
rather than triage. What triage establishes is that the premise is still real - the three
verifiers named here would still pass over a delivery that had been made inert.

## Acceptance Criteria

> **What these criteria are.** They are the DELIVERY CONTRACT for the halves that still
> reproduce, not a claim that this run built them. The operator's ruling stands: these bugs
> are triaged, not built. What the design rung produced is criteria that fail RED now, so
> whoever delivers the fix inherits a falsifiable target instead of a summary. The one
> exception is called out where it sits: a criterion pinning a half that has already LAPSED
> is a regression pin, and it goes green the moment its test exists rather than when a fix
> lands.

- [ ] **AC1** Given `tools/tests/conftest.py` with its `sys.path.insert` call DELETED, when BG0476's AC1 verifier runs, then it FAILS - today the file's own docstring mentions `sys.path.insert` at line 8, so the assertion is satisfied with the call gone.
  - **Verify:** pytest tools/tests/test_conftest_guard.py::TheGuardSeesTheCallNotTheDocstringTests::test_deleting_the_call_reddens_ac1
- [ ] **AC2** Given US0606's `lane-check` slice, when its `|| true` assertion runs, then it reads the LANE's own pipeline rather than an unrelated one - today the slice lands inside a comment block.
  - **Verify:** pytest tools/tests/test_precommit_lane_order.py::TheSliceReadsTheLaneTests::test_the_slice_is_not_a_comment_block
- [ ] **AC3** Given `best_practice_rules.py` with its practice file ABSENT, when it runs, then it refuses rather than returning 0 - an exemption reachable by deleting a file is the shape US0608 AC4 exists to prevent.
  - **Verify:** pytest tools/tests/test_best_practice_rules.py::AnAbsentPracticeFileRefusesTests::test_a_missing_file_is_not_an_exemption
- [ ] **AC4** Given the shipped gate, when its lanes are enumerated, then `best_practice_rules.py` is wired into one - it is referenced by nothing in `.githooks/` or `package.json`, so it guards nothing today.
  - **Verify:** pytest tools/tests/test_best_practice_rules.py::AnAbsentPracticeFileRefusesTests::test_the_checker_is_wired_into_a_lane

## Steps to Reproduce

For each, apply the named mutant with `__pycache__` purged and python3 -B, and observe the declared verifiers stay green.

## Proposed Fix

Point each verifier at the behaviour: run the hook, run the command, or parse the call graph. `tools/best_practice_rules.py` should fail loudly on an absent practice file and be wired into a lane that runs.

## Impact

Four more criteria that cannot fail. Individually small; together they are why five review passes returned 27 rejections against a batch whose every declared verifier was green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
