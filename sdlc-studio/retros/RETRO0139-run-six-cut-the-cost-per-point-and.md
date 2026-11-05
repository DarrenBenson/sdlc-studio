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
| BG1185 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1186 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1188 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1189 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1190 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1191 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1192 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1193 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1194 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1195 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1196 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1198 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1199 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1200 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1201 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1202 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1203 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1204 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1205 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1206 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1207 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1208 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1209 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1211 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1214 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1215 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1218 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1219 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1222 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1225 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1228 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1229 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1230 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1231 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1232 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1233 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1234 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1235 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| BG1237 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| CR0663 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |
| CR0662 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-05 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US1117 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1118 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1120 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1119 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1224 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1223 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1213 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1121 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1220 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1217 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1226 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1227 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1236 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **16740s** | - |

**0 of 13 unit(s) measured; 10 of 13 forecast at plan time.**

**Priced cost: 36,820,993 priced input-equivalent tokens**, 1,269,689 per point over 29 delivered points. Read once per message from the main thread and every subagent transcript. Each component is its count times its weight.

- input: 3,636 x1
- output: 988,495 x5
- cache write 5m: 4,490,874 x1.25
- cache write 1h: 400,972 x2
- cache read: 254,593,459 x0.1

**Sprint tokens/point: 202,896** (5,883,977 tokens over 29 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 20 pass(es) over 13 unit(s), 7 rejected
Unmeasured: US1117, US1118, US1120, US1119, BG1224, BG1223, BG1213, US1121, BG1220, BG1217. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1226, BG1227, BG1236. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->
