# RETRO-0143: Run ten: verdict binding and the report of record

> **Date:** 2026-11-12
> **Run:** RUN-01M77177
> **Batch:** BG1030, US1011, US1012, US1013, US1014, US1015, US1016, BG1010, US0997, US0998, US1000, US1001, US1147, US1134, BG1300, US1149, BG1334

## Keep

- Regrooming every unit at HEAD before planning, one engineering-seat agent per area: it corrected line references that had moved 400 to 600 lines since October and found three dependencies D0461 had not listed (BG1030, BG1010, US0997).
- Using each feature on the run's own reviews as soon as it landed: from US1011 on, every reviewer wrote the verdict file its brief named, US1016 rebuilt US1000's round-2 brief from the ledger, and US1014 named the agent that wrote each verdict.
- Fixing a regression that turned main red inside the run as a batch unit (BG1334), and holding the push until it was green, rather than waiving the failing test.
- Building BG1300 last, in the main checkout, with every other commit held: every test and mutant ran under a temporary HOME and /home/darren/.gitconfig never existed.

## Stop

- Stop grooming a unit's Affects from its own files only: five units (US1011, US1149, US0997, US1012, US1000) reached a test outside their Affects, two of them tests another unit had landed earlier in the same run.
- Stop resuming a large builder context for a small repair: US1149 and US1012 each cost about 2.3M to 2.4M priced tokens because a 190k-token context was re-read to make a one-test change.
- Stop collapsing a criterion's Verify lines without timing the result: US1134's AC4 became one line of 17 modules that needs a 530 s timeout, and the stacked lines it replaced had already turned main red.

## Try

- At grooming and again at each lane brief, grep the whole tests tree (scripts/tests and tools/tests) for every function, printed string and ledger cell the unit changes, including tests landed earlier in the run, and put each hit in Affects.
- Fast-forward every lane's worktree to main as the brief's first step and again before `lane land` commits, so a lane is judged on main's code (BG1338, BG1337).
- Send a repair to a fresh builder from the REJECT's verdict file; resume a builder only to hand it a ruling while its staged work sits in its worktree.

## Machinery share (D0442)

Delivered 17 units, 56 points: the 55 planned (D0465) and BG1334 (1, added in-run). By theme, machinery 3 points (5%): BG1300 and BG1334; evidence 35 (EP0280 with BG1030, and BG1010, US0997, US0998, US1001); cost 15 (US1000, US1134, US1149); product 3 (US1147). By path, all 56 points touch the loop scripts, .githooks/ or tools/.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1335 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1336 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1337 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1338 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1339 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1340 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1341 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1342 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1343 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1344 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1345 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1346 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1347 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1348 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1349 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1350 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1351 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1352 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1353 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1354 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1355 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1356 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1357 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1358 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1359 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1360 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1361 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1362 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1363 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1364 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1365 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1366 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1367 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1368 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1369 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1370 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1371 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1372 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1373 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1375 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1376 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1377 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1378 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1379 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1380 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1381 | not-stop-ship | orchestrator | 2026-11-12 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG1030 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1011 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1012 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1013 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1014 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1015 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1016 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1010 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0997 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0998 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1000 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1001 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1147 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1134 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1300 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1149 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1334 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 17 unit(s) measured; 16 of 17 forecast at plan time.**

**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with

**Sprint tokens/point: 148,036** (8,290,038 tokens over 56 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 22 pass(es) over 17 unit(s), 5 rejected
Unmeasured: BG1030, US1011, US1012, US1013, US1014, US1015, US1016, BG1010, US0997, US0998, US1000, US1001, US1147, US1134, BG1300, US1149. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1334. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->
