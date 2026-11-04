# RETRO-0138: Run five delivered the release path and the Cursor meters, at a cost the operator ruled too high

> **Date:** 2026-11-04
> **Run:** RUN-01M6F74P
> **Batch:** BG0958, BG1090, BG1114, BG1116, BG1122, BG1147, BG1160, BG1163, BG1167, US1112, US1113, US1114, US1115, US1116, BG1183, BG1187, US0989, US0990, US0991, BG1197, BG1210, BG1212, BG1216

## Keep

- Building in parallel waves of units with no shared files, with small units sharing one lane and one reviewer (D0404): 19 points landed in about four hours after it, against 14 in the 35 hours before, and agent tokens per point fell from about 200K to about 140K.
- Resuming the original builder for a repair, in a worktree recreated at the same path, and briefing it on the blocking findings only: BG1116, BG1163, US0990 and BG1183 each closed at round 2 that way.
- Letting the review cap carry a unit that did not converge: US0986 went to BG1205 rather than a third round, and the blocking part of it shipped in the run as BG1197.
- Pushing to the gate host mid-run: the full suite there caught four regressions no commit hook selected (the PRD and TSD rows for the Cursor call, the wall-clock census, a shell-hazard false positive), each fixed in the run as BG1210, BG1212, BG1216 and a re-spaced quote.

## Stop

- Asking the operator mid-run: four questions in one day stopped the run before D0404 ruled that sprints decide, record and list their rulings at the sign.
- Running four or five agents at once on a four-core laptop: load reached 15 to 35, commit hooks took 15 to 40 minutes, two commits hit their ceiling, and BG1183's primer tests and every timing-bound criterion flaked under it.
- Briefing a repair on every finding: US1112's repair was asked for all seven, against the lane brief's rule that a repair carries only the blocking ones and files the rest.
- Grooming a timing bound this laptop meets only when idle: BG1183 AC2 (120 s) and BG1187 (120 s) each passed only at load below about 10.

## Try

- Run builders' test passes and commit hooks on the gate host (CR0661), so parallel lanes stop competing for four local cores.
- Before landing any change to a PRD or TSD NFR, run tools/tests/test_lean_prd_refresh.py and test_lean_tsd_refresh.py together: a one-paragraph PRD fix (BG1210) broke the TSD test (BG1216).
- Measure the run's priced cost at each wave, not only at the close: the operator's 1M-per-point norm was missed by three times before anyone measured it.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1185 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1186 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1188 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1189 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1190 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1191 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1192 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1193 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1194 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1195 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1196 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1198 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1199 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1200 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1201 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1202 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1203 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1204 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1205 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1206 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1207 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1208 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1209 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1211 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1213 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1214 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1215 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1217 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1218 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1219 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| CR0661 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| CR0662 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1220 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0958 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1090 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1114 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1116 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1122 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1147 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1160 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1163 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1167 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1112 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1113 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1114 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1115 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1116 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1183 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1187 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0989 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0990 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0991 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1197 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1210 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1212 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1216 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 23 unit(s) measured; 15 of 23 forecast at plan time.**

**Priced cost: 144,830,680 priced input-equivalent tokens**, 2,540,889 per point over 57 delivered points. Read once per message from the main thread and every subagent transcript. Each component is its count times its weight.

- input: 7,676 x1
- output: 2,096,736 x5
- cache write 5m: 41,067,170 x1.25
- cache write 1h: 847,822 x2
- cache read: 813,097,176 x0.1

**Sprint tokens/point: 772,270** (44,019,404 tokens over 57 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 30 pass(es) over 23 unit(s), 7 rejected
Unmeasured: BG0958, BG1090, BG1114, BG1116, BG1122, BG1147, BG1160, BG1163, BG1167, US1112, US1113, US1114, US1115, US1116, BG1183. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1187, US0989, US0990, US0991, BG1197, BG1210, BG1212, BG1216. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->
