# RETRO-0159: Open bugs fall under fifty as forty-six Lows are fixed; each fix's test fails without it

> **Date:** 2026-11-25
> **Run:** RUN-01M87B5M
> **Batch:** BG0952, BG0969, BG0973, BG1006, BG1013, BG1017, BG1068, BG1103, BG1128, BG1151, BG1152, BG1193, BG1237, BG1287, BG1292, BG1307, BG1328, BG1342, BG1389, BG1424, BG1427, BG1454, BG1476, BG1495, BG1589, BG1594, BG1595, BG1616, BG1619, BG1641, BG1657, BG1677, BG1695, BG1713, BG1719, BG1739, BG1026, BG1296, BG1649, BG1661, BG1449, BG1304, BG1752, BG1335, BG1251, BG1269, BG0960, BG1282, BG1412, BG1504, BG1497

## Keep

- Folding a lane's later carries into the round that is already waiting to land. SPA's round three took BG1251 and BG1269 while it waited for BG1752, so four units landed in one commit and were judged in one review pass.
- Briefing a high-risk unit's second seat in parallel with its qa carry round. BG0960's and BG1335's engineering verdicts were ready when their qa seats approved, so each closed within minutes under its ruling (D0628, D0629).
- Filing a red push gate as its own one-point unit at once. BG1752 was filed, built, landed, approved and pushed within two hours of the refusal, and nothing else waited on a hand fix.
- A reviewer fuzzing the whole input class, not the builder's cases. BG1304's round-six reviewer ran 200,000 inputs with author spans and URLs and found no touching span, against 41,705 at the base.
- Adding groomed one-point Lows when the run's own filings put the goal out of reach. Four were fixed (BG1282, BG1412, BG1497, BG1504) instead of withdrawing a filed bug to meet the number.

## Stop

- Stop staging the paperwork commit by directory without the decisions log. D0626 and D0627 sat uncommitted across two paperwork commits and a push while the ledger rows citing them went to origin (BG1757).
- Stop letting a builder add a test that reads a clock without running the wall-clock census. BG1304's two timing bounds turned the push gate red, and every commit that selected the census, until BG1752 landed.
- Stop letting a chain close a carry before the unit it carries went Fixed. carry-exit moved BG1747 to Fixed while BG1661 was held for its second seat; the script now checks the accept line first.

## Try

- [new: a high-risk carry round briefs both seats at once] When a high-risk unit carries, brief its second seat in the same step as the carry round, and prepare the joint-cap ruling before either verdict returns. Each seat's verdict is then recorded as soon as it arrives, and the unit closes in one pass instead of waiting for a second brief.
- [new: the paperwork commit stages every file a recorded row cites] Stage the decisions log with the review ledger whenever a row names a ruling. A commit then never carries a citation to a decision it does not hold.
- [new: a builder adding a timing test runs the census before hand-in] A builder that adds or moves a test which reads a clock runs `tools/tests/test_test_census.py` before hand-in. The census then refuses the bound in the builder's worktree, not at the push gate.

## Cost

- BG1304 took six build rounds. Each reviewer fuzz found one more way the escaper's code spans could touch an author's, until round six left a token bare wherever it would touch one.
- First verdicts: 36 of 51 units were rejected first time. Most findings were a sentence left untrue or an unpinned branch; eleven units carried at the cap (BG1742 to BG1751 and BG1758), and every carry closed past the cap, all but BG1744 in round three.
- The joint review cap starved four high-risk second seats at carry exit. Each needed a delegate ruling (D0626 to D0629) to record a round past the cap.
- BG1497's release note claimed more than its test checks in two rounds running: first that the test fails on any key, then on any key it cannot resolve. Each round cost a builder pass and a review, and the second carried it at the cap (BG1758).
- The push gate refused once (BG1752's census) and the paperwork commit once (uncited verdict copies left by refused accepts).
- API 529 overloads killed a builder and a reviewer mid-task; both resumed by message. Host memory pressure from another project stopped a CI watch and a builder's final full-suite run.

## Not filed (D0561, no user meets a wrong result)

- The wall-clock census does not read `time.process_time`, so a constant processor-time bound passes it (repo-only test guard).
- test_file_finding.py:443-445 marks a clock-free test serial_only and boundary_only (left by 5264ed050, harmless).
- The sdlc_md find_by_id root-spelling cache, the test_sprint_drive_wave and test_status load flakes, and the test_cli_grammar reconcile timeout under load.
- MD051 at reference-agent-prompt-template.md:14 under the root config only.
- `sprint batch swap --in` accepts an id with no file (input error).
- sprint.py close-line openings print the run-state spelling, and lanes.py:1410's report-mode APPROVE warning spacing (wording).
- A home-lane brief says `lane land` records mutants (US1201, wording).

## Machinery share (D0440)

Delivered all 51 units: the 46 planned Lows, BG1752 (the push gate's own red) and four groomed Lows, and closed the eleven carries the review cap opened on them. By theme the run is almost all machinery: the units fix the skill's own sprint, lane, review, cost and prose tooling (sprint.py, lanes.py, critic.py, token_meters, the prose escaper, reference-config.md), which every user of the installed skill runs at plan, build, review and close, so each one is a defect a user can meet. Closing them takes the open count from 92 to 46, five of those filed from this run's reviews.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1753 | not-stop-ship | orchestrator | 2026-11-25 |
| BG1754 | not-stop-ship | orchestrator | 2026-11-25 |
| BG1755 | not-stop-ship | orchestrator | 2026-11-25 |
| BG1756 | not-stop-ship | orchestrator | 2026-11-25 |
| BG1757 | not-stop-ship | orchestrator | 2026-11-25 |

All five are Low and filed from this run's reviews. BG1753 lets a high-risk unit go Fixed on one seat's round-two approval after the other seat rejected it; BG1754 leaves a story Blocked after its last blocking decision is resolved; BG1755 lets a bare URL's code span touch an author's; BG1756 names the wrong template in one plan refusal; BG1757 lets a commit stage a ledger row citing a decision it does not carry. None changes a release outcome.

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0952 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0969 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0973 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1006 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1013 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1017 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1068 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1103 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1128 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1151 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1152 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1193 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1237 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1287 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1292 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1307 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1328 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1342 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1389 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1424 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1427 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1454 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1476 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1495 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1589 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1594 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1595 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1616 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1619 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1641 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1657 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1677 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1695 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1713 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1719 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1739 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1026 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1296 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1649 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1661 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1449 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1304 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1752 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1335 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1251 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1269 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0960 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1282 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1412 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1504 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1497 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **292728s** | - |

**0 of 51 unit(s) measured; 46 of 51 forecast at plan time.**

**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with

**Sprint tokens/point: 430,099** (33,117,619 tokens over 77 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 123 pass(es) over 51 unit(s), 48 rejected

Second review seats on 24 high-class unit(s) - read from the verdict ledger:

  second seat engineering: caught 7 of 24 unit(s) after the first seat approved: BG0969, BG1287, BG1649, BG1335, BG1251, BG1269, BG0960
Unmeasured: BG0952, BG0969, BG0973, BG1006, BG1013, BG1017, BG1068, BG1103, BG1128, BG1151, BG1152, BG1193, BG1237, BG1287, BG1292, BG1307, BG1328, BG1342, BG1389, BG1424, BG1427, BG1454, BG1476, BG1495, BG1589, BG1594, BG1595, BG1616, BG1619, BG1641, BG1657, BG1677, BG1695, BG1713, BG1719, BG1739, BG1026, BG1296, BG1649, BG1661, BG1449, BG1304, BG1335, BG1251, BG1269, BG0960. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1752, BG1282, BG1412, BG1504, BG1497. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M87B5M.

engineering has adverse evidence (bug:BG1754, bug:BG1756) and no learning listed.

qa has adverse evidence (round:BG1287r2, round:BG1649r3, round:BG1251r3, round:BG1269r3, bug:BG1752, bug:BG1754, bug:BG1756, bug:BG1755) and no learning listed.

0 of 123 verdict rows name no seat.
<!-- persona-learnings:end -->
