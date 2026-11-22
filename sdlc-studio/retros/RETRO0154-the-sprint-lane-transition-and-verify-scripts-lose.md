# RETRO-0154: The sprint, lane, transition and verify scripts lose 32 Medium bugs; each fix's test fails without it

> **Date:** 2026-11-22
> **Run:** RUN-01M7YPFD
> **Batch:** BG0983, BG0985, BG0987, BG1021, BG1051, BG1058, BG1400, BG1406, BG1413, BG1448, BG1491, BG1512, BG1539, BG1582, BG1590, BG1610, BG1629, BG0981, BG0961, BG1023, BG0954, BG0956, BG1107, BG1399, BG1409, BG1614, BG1624, BG1627, BG1609, BG1470, BG1477

## Keep

- One repair lane per shared file. Rejected units were repaired in lanes grouped by the file they share (sprint.py, lanes.py, transition.py, verify_ac.py), so each repair landed as one commit through one hook run and the reviewer who rejected re-checked them together.
- One ruled round past the cap where a single test or sentence was left. Fourteen rulings (D0565 to D0578) each admitted one round past the cap of two; thirteen units converged in it and only BG1534 did not, which is far cheaper than carrying a unit one test short of done to the next run.
- The rejecting reviewer re-running its own scenario and mutants in the next round. Round two caught real regressions inside repairs: BG1399 (another worktree's Affects edit not read), BG1614 (a saved brief with no BRIEF line refusing rejoinders) and BG1477 (a kept split recording a given --minutes whole, so a 30-minute builder read 60).
- Filing only what a reviewer confirmed already held at the run base with no open bug covering it (BG1692, BG1695, BG1696), and adding new evidence to an open bug rather than filing a duplicate (BG1230, BG1342).

## Stop

- Stop handing in a diff whose new lines are not each pinned. 27 of the 31 first reviews rejected, almost all on a branch, guard or sentence in the unit's own diff with no test that fails without it. The self-review section added to the builder prompt mid-run (every changed line through the mutation pass, every sentence in the Affects re-read) cut the round-two rejections but did not stop them.
- Stop landing while the workstation is loaded. Two landings were stopped at the 1800-second commit bound with the load above 12 (the lanes repair and lane X), and one prose-only landing failed on a timing test that reads a pid file before the child writes it (BG1694); each was landed on a retry once the load fell.
- Stop leaving a built lane waiting while repairs in the same files land ahead of it. Lane X waited behind four landings in lanes.py and test_lane_land.py, then conflicted in both and needed a builder to carry it onto main, and the replay found a refusal message ('no hook ran') that the BG1409 work had made untrue.

## Try

- Gate the self-review: have the land's self-check judge refuse a hand-in whose mutation pass does not cover every changed hunk in the unit's Affects, not only the criteria's lines.
- Land lanes that share a file in the order they were briefed, and give a lane that waits behind another landing in the same file a rebase step before its own land.
- Return a unit approved in a ruled round past the cap to the batch, with its carry bug moved to Fixed, so the close credits it without hand work (BG1698; 13 units were re-added by hand this run).

## Cost

- The cause is repair rounds. The verdict ledger holds 71 review passes over 31 units, 40 of them rejections: 27 of the 31 first reviews rejected, under D0561's rule that a [new] finding in the unit's own diff blocks, and 14 units needed a ruled third round. Each repair round paid for a builder and a reviewer again, so the run cost about two and a half rounds per unit where the plan priced one.
- Lane X was built once, carried onto main by a second builder after it conflicted with repairs that landed first, and then repaired in two lanes, so its eight units paid for three builds before review converged.
- Four landings were re-run (two at the commit bound under load, one replay conflict, one timing-test failure). These cost elapsed time and gate-host minutes more than tokens.

## Machinery share (D0440)

Delivered 31 units, 79 points, all bugs, all Medium; BG1534 (3 points) is carried open after its ruled third round rejected. By theme the whole run is product: every unit's Affects lies in the shipped skill's scripts (sprint.py, lib/lanes.py, transition.py, verify_ac.py, critic.py, sprint_report.py, lib/drive.py), their tests and reference pages, and changelog fragments, none in tools/ or this repository's CI. The batch held 32 at plan; BG1569 was swapped out for BG0981 (re-sized for run twenty-two with BG1678); 14 units were dropped at the review cap and 13 of them, approved in their ruled third rounds, were added back.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1534 | deferred | orchestrator | 2026-11-22 |
| BG1682 | deferred | orchestrator | 2026-11-22 |
| BG1676 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1677 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1678 | deferred | orchestrator | 2026-11-22 |
| BG1679 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1692 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1694 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1695 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1696 | not-stop-ship | orchestrator | 2026-11-22 |
| BG1698 | not-stop-ship | orchestrator | 2026-11-22 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0983 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0985 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0987 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1021 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1051 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1058 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1400 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1406 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1413 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1448 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1491 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1512 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1539 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1582 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1590 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1610 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1629 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0981 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0961 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1023 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0954 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0956 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1107 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1399 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1409 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1614 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1624 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1627 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1609 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1470 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1477 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 31 unit(s) measured; 30 of 31 forecast at plan time.**

**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with

**Sprint tokens/point: 214,283** (16,928,343 tokens over 79 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 71 pass(es) over 31 unit(s), 40 rejected

Second review seats on 23 high-class unit(s) - read from the verdict ledger:

  no second-seat verdict on BG0983, BG0985, BG0987, BG1021, BG1051, BG1058, BG1400, BG1406, BG1448, BG1491, BG1512, BG1582, BG1590, BG1629, BG0981, BG0961, BG1023, BG0954, BG0956, BG1107, BG1609, BG1470, BG1477: one seat reviewed each
Unmeasured: BG0983, BG0985, BG0987, BG1021, BG1051, BG1058, BG1400, BG1406, BG1413, BG1448, BG1491, BG1512, BG1539, BG1582, BG1590, BG1610, BG1629, BG0961, BG1023, BG0954, BG0956, BG1107, BG1399, BG1409, BG1614, BG1624, BG1627, BG1609, BG1470, BG1477. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0981. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M7YPFD.

qa has adverse evidence (bug:BG1676, bug:BG1677, bug:BG1679, bug:BG1692, bug:BG1695, bug:BG1696) and no learning listed.

0 of 71 verdict rows name no seat.
<!-- persona-learnings:end -->
