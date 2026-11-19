# RETRO-0151: A second review seat earns its cost on the paths a builder never walks, and a run's own side jobs can starve its landings

> **Date:** 2026-11-19
> **Run:** RUN-01M7SS62
> **Batch:** BG1605, BG1607, BG1622, US1192, US1193, US1195, US1196, US1197, US1198, US1200, US1201, US1202, US1236, US1237, US1238

## Keep

- The engineering second seat on the nine high-risk units (D0523, D0540). It rejected five of the nine, and every blocking finding was reproduced through the shipped CLI. Six of those defects were ones the qa seat had approved or rated non-blocking: US1192's dropped builder commits and lost commit log, US1202's equal time limits, US1238's module-only id, US1196's landing that could not resume, and US1198's lost unit. The qa seat in turn blocked US1201 on a defect the engineering seat rated non-blocking, so neither seat alone would have caught all of them.
- Repairing against a brief that quotes the REJECT verbatim. US1195 landed in wave one and briefed its own run's four repair rounds (US1192, lane five and lane six), and each repair builder fixed exactly the blocking findings and filed the rest (BG1626, BG1627).
- Landing several worktrees as one commit (US1192) from the run that built it. Lane five landed with US1192's repair, and lane six with BG1622, each through one hook run.
- Tracing a gate refusal to its exact lines before acting. The noise budget's refusal was reproduced at both commits, and the detector's per-line record was diffed for test_sprint, so the two leaked warnings were named and BG1622 was filed in one pass, with no budget raised.

## Stop

- Stop running suite-sized jobs on the machine while a `lane land` commits. My noise comparison ran beside the lane five landing and pushed its hooks past lane land's 1800s limit; the hook tree was orphaned (BG1610) and had to be killed by PID before a resume.
- Stop staging `sdlc-studio/` whole while a reviewer is still writing its verdict file. Paperwork commit 294770b0 swept in two reviewers' in-progress verdict files; they happened to be final, which is luck, not a rule.
- Stop shipping a new stderr line from a command the tests run in-process without running the noise gate on its callers. BG1605's unmetered warning leaked from two test_sprint tests, and the green-run noise gate refused every push from a5809780 until BG1622 was folded in.
- Stop writing a code span with an edge space in a verdict file (run seventeen said this too). US1198's round-two verdict was refused by `critic.py record` on MD038, and the reviewer had to be resumed to correct its own file (CR0747).
- Stop waiting on a background job with `pgrep -f` on a string from the waiter's own command line. The US1192 repair builder left such a loop matching itself, and it held the worktree until it was killed.

## Try

- Give a landing the machine to itself: start no suite-sized job until `lane land` reports, at least until BG1610 makes a timed-out commit end its own hooks.
- Run `verify_ac` after `critic.py record`, never between a brief and its record. The verify stamps the criteria and changes the brief's fingerprint, so the record then warns of a scope change that is only a stamp (BG1614).
- When a unit adds a line to stderr of a command the tests call in-process, its builder runs `tools/run-suite.sh --noise-gate` on the modules that call it before hand-in, the check BG1622 needed.

## Machinery share (D0440)

Delivered 15 units, 48 points: the 14 planned (47 points) and BG1622, folded in by re-plan when its noise held every push (1 point). By theme it is all process machinery. It is the delivery loop's own cost tooling: the wave driver and the one-step hand-back, landing and repair, the machine-run mutants and their replay, the CI red-run rules, and the run's cost meter. That is the share the operator chose with "Cost per point first" (D0537), serving O11 and End goal 3. No maintenance declaration was recorded at plan, because nothing yet computes the share or asks for one; CR0722, with US1280 and US1281 in Draft, is that tooling.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1609 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1610 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1611 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1612 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1613 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1614 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1615 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1616 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1617 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1618 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1619 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1620 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1621 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1623 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1624 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1625 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1626 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1627 | not-stop-ship | orchestrator | 2026-11-19 |
| BG1628 | not-stop-ship | orchestrator | 2026-11-19 |
| CR0746 | not-stop-ship | orchestrator | 2026-11-19 |
| CR0747 | not-stop-ship | orchestrator | 2026-11-19 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG1605 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1607 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1622 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1192 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1193 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1195 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1196 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1197 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1198 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1200 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1201 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1202 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1236 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1237 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1238 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 15 unit(s) measured; 15 of 15 forecast at plan time.**

**Priced cost: 46,289,662 priced input-equivalent tokens**, 964,368 per point over 48 delivered points. Read once per message from the main thread and every subagent transcript. Estimated US dollars: $126.81, $2.64 per point, covering 100.0% of the priced tokens; price table effective 2026-11-12. Each component is its count times its weight.

- input: 3,862 x1
- output: 1,894,460 x5
- cache write 5m: 5,351,434 x1.25
- cache write 1h: 476,072 x2
- cache read: 291,720,636 x0.1

**Sprint tokens/point: 160,955** (7,725,828 tokens over 48 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 25 pass(es) over 15 unit(s), 7 rejected

Second review seats on 9 high-class unit(s) - read from the verdict ledger:

  second seat engineering: caught 3 of 3 unit(s) after the first seat approved: BG1605, BG1607, US1195

  no second-seat verdict on US1192, US1196, US1198, US1201, US1202, US1238: one seat reviewed each
Unmeasured: BG1605, BG1607, BG1622, US1192, US1193, US1195, US1196, US1197, US1198, US1200, US1201, US1202, US1236, US1237, US1238. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M7SS62.

engineering has adverse evidence (bug:BG1610, bug:BG1622, bug:BG1628, bug:BG1616, bug:BG1618, bug:BG1619, bug:BG1620) and no learning listed.

qa has adverse evidence (round:BG1605r2, round:US1195r2, bug:BG1610, bug:BG1612, bug:BG1622, bug:BG1623, bug:BG1626, bug:BG1611, bug:BG1615, bug:BG1617, bug:BG1618, bug:BG1619, bug:BG1620, bug:BG1625) and no learning listed.

0 of 25 verdict rows name no seat.
<!-- persona-learnings:end -->
