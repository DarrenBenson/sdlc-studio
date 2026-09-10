# BG0660: the rehearsal-lane test drives the WHOLE boundary gate to check one lane's reporting, and times out on CI - main was red two days and nothing read it

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Lint run 34167594597, job 101881636181, 2026-09-07: `Ran 6885 tests in 3947.791s / FAILED (errors=1, skipped=2)`, the error a TimeoutExpired at test_gate.py:6448 through _gate at test_gate.py:6382. Local boundary gate on 2026-09-10: release-rehearsal 0.8 s, revert-check 15.7 s, module-alone 414.7 s, gate cost 515.6 s.
> **Created:** 2026-09-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`ReleaseRehearsalLaneTests` checks that the release-rehearsal lane NAMES which half broke. To do that it runs `gate.py --root <clone> --boundary push` as a subprocess with a 1800-second timeout. That invocation pays every lane the push boundary binds, which since US0666 wrote this test has grown to include `revert-check` and `module-alone` - and `module-alone` alone is 415 seconds on this machine. On the CI runner the whole gate exceeded the 30-minute timeout and the suite errored: `subprocess.TimeoutExpired`, one error, 6,885 tests in 3,948 seconds, job wall clock 1 h 7 m. The class is `@boundary_only` precisely because it was 24% of the per-commit suite; the cost it was moved to escape has since quadrupled at the boundary it was moved to.

## Steps to Reproduce

1. Push to main so the Lint workflow runs the full suite.
2. Read the ci job: ERROR `test_the_rehearsal_lane_names_its_failing_half_and_records_its_cost`, subprocess.TimeoutExpired after 1800 s.
3. Locally, run `gate.py --boundary push` and read the lane costs: module-alone 415 s, gate cost 516 s against a 45 s budget. CI is roughly five times slower.
4. Run 34167594597 (2026-09-07) is the instance; it was the latest push-triggered Lint run on main for two days and no push crossed the boundary in that time, so nothing read it.

## Proposed Fix

Scope the invocation to the lane under test. `gate.py --only release-rehearsal --boundary push` runs the one lane whose reporting this class asserts on, at the cost of a stub script that exits immediately, instead of paying revert-check and module-alone to observe neither. Keep one unscoped invocation if the class also means to assert that the boundary binds the lane at all, and give that one a timeout derived from the recorded boundary figure rather than a literal.

## Acceptance Criteria

- [ ] **AC1** Given the reporting check for the release-rehearsal lane, when it drives the gate, then the output carries that lane and NEITHER of the other two the push boundary binds. The existing assertions - the lane failed, it named its greenfield half, it recorded a duration - all pass on an unscoped run too, so none of them can say whether the check pays for one lane or for all of them, which is the whole of this bug
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseRehearsalLaneTests::test_the_check_pays_for_one_lane_and_not_the_whole_boundary
- [ ] **AC2** Given the same check scoped, when it runs, then the lane still FAILS, still names the half that broke and still records its duration. The paired control: a scope so narrow that the lane never runs satisfies AC1 perfectly and measures nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseRehearsalLaneTests::test_the_rehearsal_lane_names_its_failing_half_and_records_its_cost
- [ ] **AC3** Given every test module in both suites, when they are scanned, then NO test drives the boundary gate without scoping it to a lane. The class rather than the one instance: the next such invocation costs the same hour, and an enumerated exemption exempts whichever is added next. Judged over the source deliberately - the rule is about what a test invokes, and the only behavioural check is to pay the hour the rule exists to prevent
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BoundaryGateIsNeverDrivenUnscopedTests::test_no_test_drives_the_boundary_gate_without_scoping_it

- [ ] **AC4** Given a fixture holding one unscoped gate invocation and one properly scoped one, when the scan runs over it, then it sees BOTH and names only the unscoped one. AC3 is green on a clean tree whatever the scan does - a scanner that reports nothing passes it perfectly - so this row is the only thing that says AC3 would fire
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BoundaryGateIsNeverDrivenUnscopedTests::test_the_scan_finds_an_unscoped_invocation_when_there_is_one

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/tests/test_gate.py, widen the reporting check's `--only` value to name a second boundary lane | Given the reporting check for the release-rehearsal lane, when it drives the gate, then the output carries that lane and NEITHER of the other two the push boundary binds |
| AC2 | in .claude/skills/sdlc-studio/scripts/tests/test_gate.py, replace `release-rehearsal` in that `--only` argument with `duplicate-id` | Given the same check scoped, when it runs, then the lane still FAILS, still names the half that broke and still records its duration |
| AC3 | in .claude/skills/sdlc-studio/scripts/tests/test_gate.py, delete the `--only` argument from the sibling binding check's `_gate` call | Given every test module in both suites, when they are scanned, then NO test drives the boundary gate without scoping it to a lane |
| AC4 | in `.claude/skills/sdlc-studio/scripts/tests/test_gate.py`, replace the `yield` in `_boundary_calls` with `continue` so the scan reports nothing | Given a fixture holding one unscoped gate invocation and one properly scoped one, when the scan runs over it, then it sees BOTH and names only the unscoped one |

## Impact

Main was red for two days on a timeout that says nothing about the code, and the green-run noise gate never ran because the suite errored before it - so a second defect could have ridden in unseen behind the first. The pre-push red-CI read (D0181) is what surfaced it, on the first push in 34 commits.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | Claude Opus 5 | Filed |
| 2026-09-10 | Claude Opus 5 | Delivered. Scoped to the lane under test, which the file already had two precedents for: a sibling row drives `--boundary <b> --only release-rehearsal` to prove binding, and another proves that form is accepted rather than refused. Measured on this machine, both forms: 0.23 seconds scoped against 1800.42 seconds unscoped, the latter being the test's own timeout expiring rather than a run completing. The same expiry errored CI twice - 2026-09-07 and again on the push of 2026-09-10 - and both times the suite stopped there, so the green-run noise gate never ran at all. AC3 guards the CLASS: no test in either suite may drive the boundary gate unscoped, because the next one added costs the same hour. Three mutants, three killed |
| 2026-09-10 | Claude Opus 5 | Two corrections found by running the mutants rather than declaring them. AC3's first mutant - narrowing the scanned roots - SURVIVED: on a clean tree there is no offender in the sibling suite, so dropping it changes nothing, and a mutant only detectable with a planted offender is not a mutant the corpus can carry. AC4 plants one in a fixture instead, which is what says AC3 would fire at all. The scan itself was twice wrong and twice measured: it flagged an `assertIn` naming the flag in help text, and it flagged `critic.py supersede --boundary 'operator console'`, a different flag spelled the same. It reads list and tuple arguments too, because `subprocess.run([...])` writes the argv the other way and reading only direct arguments would exempt every test that used it |
| 2026-09-10 | Claude Opus 5 | Both mutants made CHEAP, which is part of the fix rather than a convenience. The obvious mutant for AC1 - drop the lane scope - makes the test drive the very 30-minute unscoped run this unit exists to remove, so killing it costs half an hour and does so again every time the ledger drifts these rows. It widens the scope to a second boundary lane instead, which reddens the same assertion in seconds. AC3 is judged by an AST scan that never EXECUTES what it reads, so its mutant edits a different invocation altogether and costs nothing to run. A mutant nobody can afford to re-run is evidence that decays into an assertion |
