# RETRO-0147: Run fourteen: the front door, the evidence page and the effort each seat ran at

> **Date:** 2026-11-16
> **Run:** RUN-01M7GEHM
> **Batch:** BG0947, BG0998, BG1260, BG1395, BG1396, US1160, US1161, US1162, US1163, US1165, US1166, US1167, US1169, BG1177, US1164, BG1474, BG1478, BG1479, BG1480, BG1484, BG1489

## Keep

- Landing the push-blocking fix first and pushing as soon as it was accepted: BG1474 restored the build-trap classes the run thirteen close had retired, and run thirteen's signed seal went up with run fourteen's first wave rather than waiting for this close.
- Folding a reviewer's or the push gate's finding into the lane already holding the files: BG1479 (two overclaiming fragments), BG1480 (three page sentences) and BG1484 (the quiet-success regression) rode in one fixes lane with BG1478, 7 points for one builder.
- Letting the land's hooks find a regression before main does: the report lane's first land was refused on two reds (a filed report citing an uncommitted plan path), and the builder fixed them in place without a review round.
- Resuming the rejecting seat for round 2: US1160's repair was approved by the seat that rejected it, on a rejoinder brief that quoted its finding.

## Stop

- Stop accepting a lane's per-commit test selection as proof a change is safe for main: BG1395's new total line passed its lane and turned test_quiet_success red at the push boundary, refusing the push a second time.
- Stop writing a criterion with no Verify line: BG1479's AC3 had none, so its accept moved the bug to Fixed and then reported it blocked until a manual line was added.
- Stop committing records with a sweeping add while a reviewer is still writing its verdict: US1161's verdict was committed half-corrected (BG1492).
- Stop leaving a builder unwatched for hours: the sweep lane's first builder stalled for 2 h 10 min with nothing written, and was found only by hand (CR0711).
- Stop grooming a unit that adds a commit lane without its registries: US1168 needed a new script and a ruled change to the 31-lane cap, so it was dropped mid-run (D0495).
- Stop handing back a fragment or page sentence unread against its code: three wave-one units claimed more than their code did (US1162's page, BG1395's and BG1396's fragments), each caught by review (lesson class LC-018).
- Stop letting a test read the harness's environment: two critic tests fail only inside an agent session, because the session id reaches the recorded verdict's source field (BG1490, lesson class LC-020).

## Try

- [LC-019] BG1395's total line broke test_quiet_success, which no lane selected, and the push boundary refused 46db0430 (BG1484); before handing back, a builder greps the whole tests tree for every output string it changes and runs those files.
- [LC-021] The evidence lane's generated table wrote empty cells as two spaces and its land was refused under MD060, and a reviewer's verdict was refused under MD038; builders and reviewers now run the main tree's markdownlint binary on every Markdown file they write, generated ones included.
- [LC-010] The push gate passed 7c64bf26 and GitHub's Lint failed it on the green-run noise gate (112 lines against 104), because run thirteen's new author-form warning leaked from passing tests; BG1489 captured the leaks, and BG1493 makes the push gate run the noise gate so the two cannot disagree again.

## Machinery share (D0442)

Delivered 21 units, 50 points: fifteen of the sixteen planned (40 of 42 points; US1168 was dropped under D0495 because its commit lane needs a new script and a ruled change to the 31-lane cap) and six added in-run (BG1474 2, BG1478 1, BG1479 3, BG1480 1, BG1484 1, BG1489 2; D0490, D0491, D0492, D0493, D0494). By theme, the front door is 18 points (US1160, US1161, US1162, US1163, US1164, BG1177, BG1478, BG1480), evidence and cost 6 (US1165, US1166), consumer-visible correctness 13 (BG0947, BG0998, BG1260, BG1395, BG1396, BG1479), and process machinery 13, about 26% (US1167, US1169, BG1474, BG1484, BG1489), within the one-third cap. Three of the machinery units (BG1474, BG1484, BG1489) repaired reds the push gate or CI found, which no plan foresaw. By path, the front door lives in README.md, SUPPORT.md, SECURITY.md and docs/, and the machinery in gate.py, retro.py, verify_ac.py, sprint.py and the test tree.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1475 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1476 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1477 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1481 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1482 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1483 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1485 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1486 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1487 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1488 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1490 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1491 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1492 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1493 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0709 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0710 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0711 | not-stop-ship | orchestrator | 2026-11-16 |
| LC-010 | not-stop-ship | orchestrator | 2026-11-16 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0947 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0998 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1260 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1395 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1396 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1160 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1161 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1162 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1163 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1165 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1166 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1167 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1169 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1177 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1164 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1474 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1478 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1479 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1480 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1484 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1489 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 21 unit(s) measured; 15 of 21 forecast at plan time.**

**Priced cost: 39,710,601 priced input-equivalent tokens**, 794,212 per point over 50 delivered points. Read once per message from the main thread and every subagent transcript. Estimated US dollars: $108.81, $2.18 per point, covering 100.0% of the priced tokens; price table effective 2026-11-12. Each component is its count times its weight.

- input: 4,280 x1
- output: 1,670,591 x5
- cache write 5m: 4,211,526 x1.25
- cache write 1h: 536,832 x2
- cache read: 250,152,946 x0.1

**Sprint tokens/point: 128,465** (6,423,229 tokens over 50 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 24 pass(es) over 21 unit(s), 3 rejected
Unmeasured: BG0947, BG0998, BG1260, BG1395, BG1396, US1160, US1161, US1162, US1163, US1165, US1166, US1167, US1169, BG1177, US1164. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1474, BG1478, BG1479, BG1480, BG1484, BG1489. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M7GEHM.

24 of 24 verdict rows name no seat.
<!-- persona-learnings:end -->
