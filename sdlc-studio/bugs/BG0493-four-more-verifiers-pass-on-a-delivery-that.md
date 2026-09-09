# BG0493: four more verifiers pass on a delivery that has been made inert

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/conftest.py, tools/tests/test_conftest_guard.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/best_practice_rules.py, tools/tests/test_best_practice_rules.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_test_census.py
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery)

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

- [ ] **AC1** Given `tools/tests/conftest.py` with its `sys.path.insert` CALL deleted, when BG0476's AC1 verifier runs, then it FAILS. The file's own docstring names `sys.path.insert` at line 8, so today the assertion is satisfied with the call gone and the guard reads its own prose. The existing verifier hard-codes the tracked path, so the new node drives a COPY with the call removed rather than the file itself
  - **Verify:** pytest tools/tests/test_test_census.py::TheGuardSeesTheCallNotTheDocstringTests::test_deleting_the_call_reddens_ac1
  - **Verified:** yes (2026-09-09)
- [ ] **AC2** Given US0606's `lane-check` assertion, when it runs, then it is anchored on the guard's own call site. Measured, the 600-character window ends on the id-gathering pipeline at relative offset 556, because the comment carrying the literal sits above the lane's own code; moving the hook block alone leaves that window in place, so the anchor is what the fix has to change
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::LaneCheckAnchorTests::test_the_assertion_is_anchored_on_the_guards_own_call
  - **Verified:** yes (2026-09-09)
- [ ] **AC3** Given `best_practice_rules.py` with its practice file ABSENT, when it runs, then it REFUSES rather than returning zero findings. An exemption reachable by deleting a file is the shape US0608 AC4 exists to prevent
  - **Verify:** pytest tools/tests/test_best_practice_rules.py::AnAbsentPracticeFileRefusesTests::test_a_missing_file_is_not_an_exemption
  - **Verified:** yes (2026-09-09)
- [ ] **AC4** Given the shipped gate, when its lanes are enumerated, then one of them NAMES `best_practice_rules.py`. It is referenced by nothing in `.githooks/` or `package.json` today, so it guards nothing
  - **Verify:** pytest tools/tests/test_precommit_lane_order.py::PracticeRulesLaneTests::test_the_checker_is_named_by_a_lane
  - **Verified:** yes (2026-09-09)
- [ ] **AC5** Given a tree the checker REFUSES, when that lane is driven as a subprocess, then the gate refuses too, and given a tree it accepts, the lane passes. Naming a script is not running it: a lane that mentions the checker in an echo and never invokes it satisfies AC4 exactly, and this bug is about a checker that guards nothing
  - **Verify:** pytest tools/tests/test_precommit_lane_order.py::PracticeRulesLaneTests::test_the_lane_runs_the_checker_and_carries_its_exit
  - **Verified:** yes (2026-09-09)

## Steps to Reproduce

For each, apply the named mutant with `__pycache__` purged and python3 -B, and observe the declared verifiers stay green.

## Proposed Fix

Point each verifier at the behaviour: run the hook, run the command, or parse the call graph. `tools/best_practice_rules.py` should fail loudly on an absent practice file and be wired into a lane that runs.

## Impact

Four more criteria that cannot fail. Individually small; together they are why five review passes returned 27 rejections against a batch whose every declared verifier was green.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/tests/test_test_census.py, change BG0476's assertion to read the file's text rather than the imported module | Given `tools/tests/conftest.py` with its `sys.path.insert` CALL deleted, when BG0476's AC1 verifier runs, then it FAILS. The file's own docstring names `sys.path.insert` at line 8, so today the assertion is satisfied with the call gone and the guard reads its own prose. The existing verifier hard-codes the tracked path, so the new node drives a COPY with the call removed rather than the file itself |
| AC2 | in .githooks/pre-commit, delete the lane-check comment block so the guard's call becomes the first mention of the keyword | Given US0606's `lane-check` assertion, when it runs, then it is anchored on the guard's own call site. Measured, the 600-character window ends on the id-gathering pipeline at relative offset 556, because the comment carrying the literal sits above the lane's own code; moving the hook block alone leaves that window in place, so the anchor is what the fix has to change |
| AC3 | in tools/best_practice_rules.py, return 0 from `main()` on the missing-file path instead of refusing | Given `best_practice_rules.py` with its practice file ABSENT, when it runs, then it REFUSES rather than returning zero findings. An exemption reachable by deleting a file is the shape US0608 AC4 exists to prevent |
| AC4 | in .githooks/pre-commit, delete the block that invokes the practice-rules module | Given the shipped gate, when its lanes are enumerated, then one of them NAMES `best_practice_rules.py`. It is referenced by nothing in `.githooks/` or `package.json` today, so it guards nothing |
| AC5 | in .githooks/pre-commit, swap the lane body for a bare echo mentioning the module path | Given a tree the checker REFUSES, when that lane is driven as a subprocess, then the gate refuses too, and given a tree it accepts, the lane passes. Naming a script is not running it: a lane that mentions the checker in an echo and never invokes it satisfies AC4 exactly, and this bug is about a checker that guards nothing |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-09 | Claude Fable 5.1 | Delivered, and TWO of the five tests failed to kill their own mutant on the first measurement. AC5's asserted the lane's command position began with the separator, which an echo naming the module also does - it reads the argv now, so a mention is told from an invocation. AC2's asserted an or-true fallback was present in the examined block, which the 600-character slice still contained by luck once a lane was added above it - it asserts where the block BEGINS now, at the guard's own call. Both were found by running the mutant rather than by reading it, which is the discipline this whole batch was re-groomed for |
