# RETRO-0153: Persona cards meet an enforced standard, each seat's goal brief uses its own card, and persona docs match the code

> **Date:** 2026-11-20
> **Run:** RUN-01M7VNR0
> **Batch:** BG1002, BG1015, BG1472, BG1535, BG1536, US1036, US1039, US1046, US1052, US1053, US1054, US1055, US1056, US1057, US1322, BG1660, US1040, BG1655, BG1663, BG1664

## Keep

- One builder for every unit that shares a file. Lane K built BG1664, US1056, US1057 and US1322 in one worktree, and the repair lane took all three rejected units back together, so each landed as one commit through one hook run, with no rebase conflict on `persona_review.py` or `sprint.py`.
- Running the whole suite on the gate host before hand-in when a change reaches beyond its own modules. US1055's first two hand-ins each stopped on test modules outside its Affects (31, then three more); once the builder ran `run-suite.sh all` itself, no landing in the run found a red module outside a unit's Affects.
- The carry rule as shipped. BG1655 carried to BG1663 and US1040 to BG1660 at the round cap; each carry bug was groomed, built and reviewed in the same run, and the reviewer who rejected discharged the carry with an APPROVE, so no unit left the batch.
- Routing every round two to the reviewer who rejected, resumed with a fresh rejoinder brief. Every round two in the run was recorded on the first try.

## Stop

- Stop briefing a high-risk unit's second seat on the same delivery as its first seat. The round cap counts verdicts across seats, and a later round must come from the seat that rejected first, so on US1055, US1056 and US1057 the engineering seat's REJECT could not be recorded (BG1665). Three rulings (D0557 to D0559) each spent a round past the cap to get the second seat's judgement of the repair on the ledger.
- Stop finding a unit's Affects one blocked hand-in at a time. Seven units stopped on an existing test outside their Affects (BG1536, US1036, US1052 twice, US1053, BG1655, and US1055 twice), each costing a widening commit and a builder resume (CR0749).
- Stop letting a builder stay inside its Affects by patching round the limit. The first repair of US1056 and US1057 wrapped `Path.read_text` process-wide while the validators ran; widening US1057 to `validate.py` let the read be made safe where it happens.

## Try

- At grooming, run the existing test modules that import each script a unit changes, and put any that write fixtures the change touches into the Affects before the builder starts (CR0749).
- Brief a high-risk unit's second seat only after the first seat's verdict is recorded, until BG1665 lets parallel seats on one delivery count as one round.
- When a unit adds a new caller of a reader or validator, probe the new path with a malformed input (a card that is not UTF-8, an empty card, a missing card) before hand-in. Both seats found US1056 and US1057's crash this way; the builder had not tried it.

## Machinery share (D0440)

Delivered 20 units, 58 points: 11 stories (39 points) and 9 bugs (19 points), the 16 planned plus four folded in by re-plan: BG1655 (a defect US1052's review found) and BG1663 (its carry at the round cap), and BG1660 (US1040's carry) and BG1664 (BG1660's review finding). By theme, the whole run is product. 33 points went to the persona standard and its enforcement (US1039, US1046, US1052, US1053, US1055, US1057, US1322, BG1655, BG1663), 16 points to each seat's goal brief coming from its own card (US1036, US1040, US1056, BG1002, BG1015, BG1660, BG1664), and 9 points to the persona templates and references describing the shipped code (US1054, BG1472, BG1535, BG1536). No points went to the repository's own machinery, so the machinery share is 0%, inside the one-third cap.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1650 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1651 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1652 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1653 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1654 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1656 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1657 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1658 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1659 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1661 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1662 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1665 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1666 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1667 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1668 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1669 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1670 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1671 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1672 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1673 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1674 | not-stop-ship | orchestrator | 2026-11-20 |
| BG1675 | not-stop-ship | orchestrator | 2026-11-20 |
| CR0749 | not-stop-ship | orchestrator | 2026-11-20 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG1002 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1015 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1472 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1535 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1536 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1036 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1039 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1046 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1052 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1053 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1054 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1055 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1056 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1057 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1322 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1660 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1040 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1655 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1663 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1664 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **173193s** | - |

**0 of 20 unit(s) measured; 20 of 20 forecast at plan time.**

**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with

**Sprint tokens/point: 193,724** (11,235,973 tokens over 58 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 34 pass(es) over 20 unit(s), 7 rejected

Second review seats on 10 high-class unit(s) - read from the verdict ledger:

  second seat engineering: caught 5 of 5 unit(s) after the first seat approved: US1036, US1055, US1056, US1057, US1040

  second seat qa: caught 2 of 2 unit(s) after the first seat approved: BG1002, US1039

  no second-seat verdict on US1322, BG1660, BG1664: one seat reviewed each
Unmeasured: BG1002, BG1015, BG1472, BG1535, BG1536, US1036, US1039, US1046, US1052, US1053, US1054, US1055, US1056, US1057, US1322, BG1660, US1040, BG1655, BG1663, BG1664. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M7VNR0.

engineering has adverse evidence (round:BG1002r2, round:US1039r2) and no learning listed.

qa has adverse evidence (round:US1036r2, round:US1057r3, round:US1040r2) and no learning listed.

0 of 34 verdict rows name no seat.
<!-- persona-learnings:end -->
