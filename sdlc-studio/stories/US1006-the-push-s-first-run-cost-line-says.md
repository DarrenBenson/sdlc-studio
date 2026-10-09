# US1006: The push's first-run cost line says what it does not know instead of a fixed five minutes

> **Status:** Draft
> **Delivers:** CR0613
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-push, AGENTS.md, tools/tests/test_push_first_estimate.py, tools/tests/test_pre_push_hook.py, changelog.d/US1006.md
> **Epic:** EP0278
> **Points:** 2
> **Depends on:** US1005, BG0978
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer pushing from a clone that has never recorded a boundary run
**I want** the cost line the pre-push hook prints before the gate to cite this clone's own measured full-suite time where it has one, and otherwise to say no run is recorded, giving the facts that drive the length (test module count, cores, parallel or serial) and never a fixed minute figure
**So that** I set a timeout that fits this machine instead of trusting 'about five minutes' and killing a gate that was going to take most of an hour

## Acceptance Criteria

- **AC1:** Given a fixture clone with no recorded boundary run and no recorded full commit-suite run, when a branch push and then a tag push run the hook, then each cost line says no run is recorded on this clone and states no fixed number of minutes.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_no_fixed_duration_is_announced_without_a_recorded_run
- **AC2:** Given the same clone, when the push runs once with pytest-xdist hidden from python3 and once with it present, then the cost line says the suite runs serially in the first case and in parallel across the machine's cores in the second, naming the number of test modules each time.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_the_cost_line_reads_parallel_or_serial_from_the_interpreter
- **AC3:** Given a clone with no boundary-push series but a recorded `total` (full commit-suite) series, when a branch push runs the hook, then the cost line cites that series' median as a floor for this machine and still states no fixed figure.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_a_recorded_full_commit_suite_run_is_cited_as_a_floor
- **AC4:** Given AGENTS.md, when the pre-push row of its refusal table is read, then it states no fixed duration and names `gate_timing.py estimate --suite boundary-push`, and running that command from the repository root exits 0.
  - **Verify:** pytest tools/tests/test_push_first_estimate.py::FirstRunEstimateTests::test_agents_md_names_the_command_not_a_figure

## Notes

- Release: 6.2 (D0355 breakdown G4, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the literals restored: 'expect about five minutes' and 'about fifteen minutes' (pre-push:158 and :160 today)
- AC2 must fail on: the cost line hard-coding 'in parallel', or counting modules from a fixed figure rather than the suite directories
- AC3 must fail on: the cost line ignoring the clone's own full-run series and printing 'no run recorded' where a measurement exists
- AC4 must fail on: 'about five minutes' left in the AGENTS.md row (AGENTS.md:44 today)
- A recorded boundary history is unchanged: the median line from `gate_timing.py estimate` still wins when one exists (pre-push:152). With no history, `estimate` prints nothing and exits 0, which the panel re-confirmed.
- The panel's answer: never a seeded figure from another machine. A CI duration measures a different machine and repeats the 'about five minutes' error with a better source. This clone's own `total` series is a fair floor, because a full commit-suite run is most of a push.
- Reads xdist presence from the first story's check, so the cost line and the preflight make one reading of the interpreter.
- tools/tests/test_pre_push_hook.py::ThePushBoundaryHasAHookTests::test_the_hook_announces_its_cost_and_the_bypass_before_running pins both literals (lines 303-313). It is updated to the new wording and keeps its mutants: the first push still announces something, before the gate, naming the bypass; a branch push does not name the tag's lanes. BG0978 also edits this module, so this story builds after it.
- Measured: this clone's recorded boundary-push runs are 3348, 3826, 1543, 2392 and 2957 seconds, against AGENTS.md's 'about five minutes'.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G4 after the refine panel's review |
