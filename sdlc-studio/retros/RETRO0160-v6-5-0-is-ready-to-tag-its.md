# RETRO-0160: v6.5.0 is ready to tag: its notes, pages and specs say only what the code does, under the release bar

> **Date:** 2026-11-26
> **Run:** RUN-01M89MN1
> **Batch:** US1328, US1329, US1327, US1331, BG1762, BG1763

## Keep

- Filing a red push gate as its own one-point unit at once. BG1762 (an order-dependent mock in US1329's test) was filed, built, reviewed and landed within ninety minutes of the refusal, and no hand fix touched the tree.
- Grooming with seat-rendered agents while lanes build. Two seats drafted nine stories (29 points) with every Fails on executed at HEAD, and the product seat put the ownership tension to the operator instead of choosing (D0636).
- Briefing a high-risk unit's two seats in one step. BG1763's qa and product seats reviewed in parallel, so neither waited on the other.
- Keeping an open Medium's bug file out of git until it is Fixed. The release-bar test refuses an open Medium at HEAD, so committing BG1763 open would have turned the push gate red.

## Stop

- Stop writing a chain script and running it in the same call, and stop waiting on script names. Two land chains waited on themselves, one for an hour, before each was stopped and relaunched by name with no wait loop of its own.
- Stop grooming a bug for a lane without its changelog fragment in Affects. `file_finding` does not add it (refine does for stories), so BG1762's first land was refused after a three-minute commit and BG1763 went back to its builder for a fragment.
- Stop accepting a builder's timed-out full suite as a pass. US1329's order-dependent test reached main because both SPECS rounds' suites timed out on a loaded gate host, and the push gate was the first full run to see it.
- Stop leaving a carry at the shipped fixed Medium when the carried unit checks the release bar. US1331's two carries (BG1760, BG1761) each deadlocked its own criterion until re-rated Low by hand (D0632, D0634).

## Try

- [new: a bug groomed for a lane names its fragment] When a bug joins a batch, its Affects names `changelog.d/<id>.md` and the fragment's claim takes that path as its surface. The land then records the self-check on the first attempt instead of refusing it after a three-minute commit.
- [new: the page moves with the corpus] A commit that files a bug or moves one to a terminal status also re-cuts the known-issues page with `known_issues.py write`. The release tests then read a page that agrees with the corpus at every commit.
- [new: two seats' parallel REJECTs] When both seats of a high-risk unit reject in parallel, record the first REJECT and fold the second seat's findings into the repair by hand. Prepare the second seat's joint-cap ruling at the first REJECT, so its approval records without a wait, until per-seat rounds land (US1032, US1033).

## Cost

- Scope moved twice. The push gate refused an 8-point US1330, which split into the cut and US1331 (D0631); then the operator widened 6.5 (D0635), so the cut left this run for run twenty-eight.
- US1331 took four rounds across two seats; its two carries each needed a hand re-rate and a ruling (D0633) to record a round past the cap.
- First verdicts: all four stories were rejected first time, mostly for a sentence a test did not pin. BG1762 was approved first time; BG1763 was rejected in two rounds (below).
- The push gate refused twice: once on the oversized unit (US0854's split threshold), once on BG1762's order-dependent test.
- `~/code` was moved to the Trash for fourteen minutes mid-run by something outside this session; the operator restored it unchanged and the interrupted chain was rerun, not trusted.
- BG1763 took three rounds across two seats and carried at the cap (BG1766). The ledger numbers both seats' verdicts as one sequence, so the qa seat's round-one and round-two REJECTs could not be recorded beside the product seat's; their findings went into the repairs by hand, and a ruling (D0641) recorded the qa seat's round-three APPROVE.

## Not filed (D0561, no user meets a wrong result)

- `known_issues._split` counts severity case-sensitively; the 21 bugs with a lowercase severity are all Closed, so nothing reads wrong.
- `known_issues.py check --at REV` re-renders an old commit with HEAD's generator (pre-existing; the 6.4 test does the same).
- US1329's test helper bounds the front matter with no control (the reviewer ruled it not a defect).
- critic's `pytest_targets` reads no selector from a `shell python3 -m pytest` Verify line, so the brief says the criteria name none (wording).
- `file_finding.is_test_path` reads a data fixture such as `tests/fixtures/test_data.json` as a test by its stem, so the brief sends it to the hand-run route; the classification predates BG1763 and neither route suits a file that is not a test.

## Machinery share (D0440)

Run twenty-seven delivered 6.5's release paperwork as first scoped: the notes (US1327), the help and public pages (US1328), the PRD, TRD and TSD (US1329) and the known-issues disclosure under the release bar (US1331), four units that face the person answering for the release. Its two bugs are machinery: BG1762 a test-isolation fault that refused the push, and BG1763 the lane brief for a project whose tests are not pytest, which consuming projects' builders read directly (the website repository's lanes met it).

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1764 | not-stop-ship | orchestrator | 2026-11-26 |
| BG1765 | not-stop-ship | orchestrator | 2026-11-26 |
| CR0752 | not-stop-ship | orchestrator | 2026-11-26 |
| CR0753 | not-stop-ship | orchestrator | 2026-11-26 |
| CR0754 | not-stop-ship | orchestrator | 2026-11-26 |
| CR0755 | not-stop-ship | orchestrator | 2026-11-26 |

BG1764 and BG1765 are Low and in run twenty-eight's batch; CR0752 to CR0755, raised during this run (the Foundry review and the operator's ownership direction), are refined into run twenty-eight and ship in 6.5 (D0635). BG1764 leaves the cost anatomy's reviewer row empty when a reviewer is recorded with its seat; BG1765 files every carry at a fixed Medium, which deadlocked US1331's own bar criterion twice in this run.

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US1328 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1329 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1327 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1331 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1762 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1763 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **97339s** | - |

**0 of 6 unit(s) measured; 3 of 6 forecast at plan time.**

**Priced cost: not stated.** the token actual already recorded was reused, not re-captured, so no component was read again; the row keeps the Priced/pt it was recorded with

**Sprint tokens/point: 786,135** (17,294,968 tokens over 22 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 17 pass(es) over 6 unit(s), 9 rejected

Second review seats on 2 high-class unit(s) - read from the verdict ledger:

  second seat product: caught 1 of 1 unit(s) after the first seat approved: US1331

  second seat qa: caught nothing after the first seat approved, over 1 unit(s)
Unmeasured: US1328, US1329, US1327. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: US1331, BG1762, BG1763. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M89MN1.

qa has adverse evidence (round:US1331r4) and no learning listed.

0 of 17 verdict rows name no seat.
<!-- persona-learnings:end -->
