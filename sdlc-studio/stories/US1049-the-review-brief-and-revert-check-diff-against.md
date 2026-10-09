# US1049: The review brief and revert-check diff against the base a small change recorded

> **Status:** Draft
> **Delivers:** CR0626
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py, changelog.d/US1049.md
> **Epic:** EP0286
> **Points:** 3
> **Depends on:** US1047, BG1009
> **Persona:** Maya Okafor

## User Story

**As** a team lead reviewing a teammate's small change from my own clone
**I want** the brief to name the commit the change started from, and the command that shows its test fails without it
**So that** I judge exactly that change's diff, and see its criterion fail at base, without asking the author for a sha

## Acceptance Criteria

- **AC1:** Given a small-change unit with a recorded base that no run names, when `critic.py brief --unit` runs, then the brief prints `git diff <base> -- <Affects>` with that base and the `verify_ac.py revert-check --unit <id>` command.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py::SmallChangeBaseRefTests::test_the_brief_names_the_recorded_base
- **AC2:** Given the same unit, when `verify_ac.py revert-check --unit` runs with no `--base`, then it reverts the production change to the recorded base and reports which criteria go red.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py::SmallChangeBaseRefTests::test_revert_check_uses_the_recorded_base
- **AC3:** Given a unit that an open run's batch names and that also carries a recorded small-change base, when `critic.py brief` runs, then the brief prints the run's base.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py::SmallChangeBaseRefTests::test_a_run_that_holds_the_unit_keeps_its_base
- **AC4:** Given an open run whose batch does not name the unit, and no recorded base, when `verify_ac.py revert-check --unit` runs with no `--base`, then it refuses naming `small_change.py start`, rather than reverting to that run's base.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py::SmallChangeBaseRefTests::test_another_runs_base_is_not_this_units
- **AC5:** Given `review.line_coverage: block` and a small-change unit with a recorded base, when `verify_ac.py run --id <unit> --coverage` runs, then it does not refuse because no run's approved batch names the unit, and the output names the recorded base.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_small_change_base_ref.py::SmallChangeBaseRefTests::test_line_coverage_measures_against_the_recorded_base

## Notes

- Release: 6.2 (D0355 breakdown G12, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the brief reads only `run_state.unit_run_base_ref`, so a unit no run names gets no base line.
- AC2 must fail on: revert-check reads only the open run's base and refuses for want of one.
- AC3 must fail on: the unit's own field is preferred over the run that holds the unit.
- AC4 must fail on: revert-check keeps `run_state.base_ref(root)` as its fallback, measuring the unit against a run about other work.
- AC5 must fail on: coverage keeps `unit_run_base_ref`, so every project that chose `block` is shut out of the path at its terminal transition.
- One reader, `run_state.unit_base_ref(root, unit)`: the base of the run whose batch names the unit, else the unit's `Small-change` field, else empty. The brief, revert-check and `coverage_report` all call it. G7's terminal gate should call it too.
- AC5 holds whether or not `coverage` 7.10+ is installed. `coverage_report` checks the base before it looks for the interpreter (verify_ac.py:2467), so the test asserts that the no-base refusal is absent and the base is named. Without coverage the output instead says coverage is unavailable, a different refusal.
- AC4 corrects a pre-existing reach. revert-check today falls back to whichever run is open (verify_ac.py:4123), even when that run's batch does not hold the unit. The brief already refuses that case (critic.py:2545: 'a ref from a run about other work is not this unit's base').
- The brief prints the revert-check command for every unit with a base, in-run units included, from the same branch that prints `git diff <base>` (panel answer Q6). That is safe only after BG1009, hence the dependency.
- Fixtures are git trees driven through the CLIs, in the shape test_lean_brief_base_ref.py uses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G12 after the refine panel's review |
