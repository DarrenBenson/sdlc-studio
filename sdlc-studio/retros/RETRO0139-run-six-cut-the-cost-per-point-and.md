# RETRO-0139: Run six cut the cost per point and landed the efficiency tooling

> **Date:** 2026-11-05
> **Run:** RUN-01M6NH7W
> **Batch:** US1117, US1118, US1120, US1119, BG1224, BG1223, BG1213, US1121, BG1220, BG1217, BG1226, BG1227, BG1236 (BG1190 carried at the cap as BG1228)

## Keep

- Builders hand in and stop, and the orchestrator commits in the background: no builder context waited on a 17 to 50 minute hook, and builders cost 0.5M to 1.6M a lane against run five's 2.06M per point.
- Fresh builders for repairs: US1117's fresh repair cost 0.60M; BG1226's resumed builder, which also ran a 765 s test in its own context, cost 1.50M before its fresh repair added 0.44M.
- Batched landings: one commit carrying several units with one Refs: trailer each paid a hub-script hook once for five units (1,739 s) rather than five times.
- Pricing each lane from its builder's transcript (US1117), from the moment it landed: the run saw what each unit cost while it ran.
- Small repairs written by the orchestrator, then reviewed independently: US1120, BG1224, BG1226 and US1119 each closed at round 2 for a few calls.

## Stop

- Queueing landings with `pgrep -f` waits: each waiter's own command line matched the others', and five queued landings deadlocked for an hour.
- Trusting per-commit selection for repo-wide sweeps: five census tests, the docgen drift tests and the help-text sweep were red on main after landings whose own hooks passed; the push gate's full suite found them.
- Passing text to `--rejoinder`: it takes the prior verdict file.
- Running a long test inside a builder or reviewer: a wait over five minutes re-pays its whole context.

## Try

- Run the commit-time suites on the gate host (CR0663): the hooks, not the agents, were this run's wall-clock.
- Run each batch's repo-wide census sweeps (test_test_census, test_root_census, test_gitutil's sweep, test_skill_tests_env, test_commit_msg_hook's hermeticity test, docgen checks) once before landing it, rather than learning of them at push.
- Start each run in a fresh orchestrator session: the main thread was a third of this run's cost at an average context near 400k.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
