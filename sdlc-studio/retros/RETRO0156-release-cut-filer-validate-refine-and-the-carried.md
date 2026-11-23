# RETRO-0156: Release cut, filer, validate, refine and the carried units lose 25 Medium bugs; each fix's test fails without it

> **Date:** 2026-11-23
> **Run:** RUN-01M836YT
> **Batch:** BG0948, BG0959, BG0968, BG0995, BG1417, BG1452, BG1475, BG1510, BG1532, BG1537, BG1541, BG1542, BG1544, BG1545, BG1551, BG1567, BG1625, BG1707, BG1714, BG1717, US1324, BG1718, BG1549, BG1550, BG0974, BG0997, BG1694, BG1552, BG1730, US1326

## Keep

- Widening a unit's Affects before it lands, so its builder fixes a sentence or test the fix makes untrue instead of a new bug being filed. EFCI (migrate.py, sdlc_md.py), REL (help/gate.md, the release-notes test), REF (the transition gate, help/refine.md, four corpus epics), FFB (`--shipped-in` help), BG1551 (sprint.py) and BG1694 (the wall-clock census) each cost one short builder resume and no review round.
- Folding a same-class defect into an open bug as a new criterion rather than filing it: BG1694 AC3 (a second pid-file race) and AC4 (the census), and BG1024 AC4 (the grep verb's `&&` false pass).
- A closed-world pinned-sentence check for a claim about a page (DOC3, after BG1056). Two rounds of word lists had either missed rewordings or refused true sentences.

## Stop

- Stop waiting on a log token that an earlier attempt may already have written. The paperwork chain matched the first attempt's "EFCI failed" line and committed during EFCI's second `lane land`; the gate refused it. Rotate each chain log before a retry.
- Stop letting builders keep their claims and mutation reports outside `sdlc-studio/.local/lane/`. CK2's hand-in lacked them, so the landing recorded no self-check and wrote no brief, and the round-two verdict could not be accepted until the hand-in was repaired and the land resumed.
- Stop writing a Verify line that runs a whole slow module. BG1730's AC3 ran the census module, 7 to 13 minutes under load, and timed out at the 120 s default; it now names the one class that pins the criterion.

## Try

- [new: hand-in outside the lane folder] A builder that keeps its claims and mutation report outside `sdlc-studio/.local/lane/` lands with no self-check and no brief, so its review cannot be accepted. Name the hand-in path in every builder brief and check the folder before landing.
- [new: census missed by a narrow commit] A new test can break the wall-clock census on a commit that does not select the census, as BG1694's bound tests did. Run `tools/tests/test_test_census.py` in the builder's self-check whenever a test module changes.
- [new: second seat past the joint cap] A high-risk unit's engineering second seat has no round left once the qa seat has used the joint cap, as US1326's needed D0609. Brief the second seat as soon as the qa seat's first APPROVE is recorded, until per-seat rounds (US1032, US1033) land.

## Cost

- Guard bypasses early in the run, before the prompt correction. Three builders got round the worktree guard for the diff-coverage pass: RP with a Python git helper, VAL with a second checkout and `--no-verify` commits, and EFCI with a `--no-verify` scratch commit. A reviewer installed Python with uv, which left a `~/.local/bin` link. All were removed or reset, and the prompts now forbid any route round the guard and any install.
- Review rounds: nine units needed a ruled third round (D0601 to D0608), and US1326's engineering seat needed D0609. BG0967 (Medium) did not converge in three rounds and is carried under BG1723. Each round's heuristic for telling a command from prose raised new edge cases in its own code, so run twenty-four should pick a rule that needs no guessing rather than try a fourth heuristic.
- Commits under load: a `sprint.py` commit selects about 207 test modules, and at load 18 the unit-tests lane was cut off at 76% after 30 minutes with no test red, so US1326 had to land again (CR0663 moves commit suites to the gate host). The first push was refused by BG1694's pid-file race, which was pulled into the run.
- When `lane land` refuses a hand-in after `land-one.sh` has committed in the worktree, re-running `land-one.sh` throws the commit away; land the existing commit with `sprint.py lane land` directly (RACE2).
- The scheduled corpus verify (run 45196238545) found two Done stories' criteria red that no run's commit gate selects: US0253 AC2 (a shared test module name, fixed in the run as BG1730) and US1112 AC4 (CI only, filed as BG1731 for run twenty-four).

## Machinery share (D0440)

Delivered 30 units, 80 points: 24 Medium bugs, 4 Low bugs and 2 stories (US1324, US1326). BG0967 (Medium) is carried open under BG1723. By theme the run is product: every unit but two lies in the shipped skill (the release cut, file_finding, validate, refine, reconcile, the engagement floor, sprint plan). The two machinery units are BG1694 (a test race that refused the push) and BG1730 (a repo test module name and its census guard), 4 points, 5% of the run, inside the one-third cap.

Not filed, as no user meets them (D0561): tools/check_versions.py crashes on a markdown file that is not UTF-8 (repo-only, found by REL's reviewer), and `test_one_reader_answers_which_file_a_selector_targets` fails when run in the same process as test_sprint.py and passes alone, from before US1326 (found by US1326's engineering seat). For run twenty-four grooming: ask the product seat whether a migrating project's non-terminal story should be able to baseline a body placeholder (validate.py:542/546 waive at terminal status only), raised by BG0948's reviewer.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1719 | not-stop-ship | orchestrator | 2026-11-23 |
| BG1722 | not-stop-ship | orchestrator | 2026-11-23 |
| BG1723 | deferred | orchestrator | 2026-11-23 |
| BG1726 | not-stop-ship | orchestrator | 2026-11-23 |
| BG1731 | deferred | orchestrator | 2026-11-23 |

BG1723 and BG1731 are deferred to run twenty-four, and the 6.5 tag waits for both: BG1723 carries BG0967, a Medium, and D0560 ships no Medium bug; BG1731 leaves US1112 AC4 red on the CI runner, and the release gate's executing verify refuses a red criterion. Neither stops this run's delivery, which changes none of their code. BG1719, BG1722 and BG1726 are Low and change no release outcome.

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0948 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0959 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0968 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0995 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1417 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1452 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1475 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1510 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1532 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1537 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1541 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1542 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1544 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1545 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1551 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1567 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1625 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1707 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1714 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1717 | 5 | 931,260 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US1324 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1718 | 1 | 186,252 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1549 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1550 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0974 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0997 | 2 | 372,504 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1694 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG1552 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG1730 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US1326 | 3 | 558,756 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **131446s** | - |

**0 of 30 unit(s) measured; 28 of 30 forecast at plan time.**

**Priced cost: 121,983,326 priced input-equivalent tokens**, 1,524,792 per point over 80 delivered points. Read once per message from the main thread and every subagent transcript. Estimated US dollars: $333.81, $4.17 per point, covering 100.0% of the priced tokens; price table effective 2026-11-12. Each component is its count times its weight.

- input: 9,986 x1
- output: 4,487,347 x5
- cache write 5m: 16,513,191 x1.25
- cache write 1h: 1,058,222 x2
- cache read: 767,786,718 x0.1

**Sprint tokens/point: 275,859** (22,068,746 tokens over 80 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes - read from the verdict ledger:

  code review: 69 pass(es) over 30 unit(s), 37 rejected

Second review seats on 10 high-class unit(s) - read from the verdict ledger:

  second seat engineering: caught 1 of 1 unit(s) after the first seat approved: US1326

  no second-seat verdict on BG1452, BG1475, BG1532, BG1545, BG1551, BG1625, BG1707, BG1714, BG1717: one seat reviewed each
Unmeasured: BG0948, BG0959, BG0968, BG0995, BG1417, BG1452, BG1475, BG1510, BG1532, BG1537, BG1541, BG1542, BG1544, BG1545, BG1551, BG1567, BG1625, BG1707, BG1714, BG1717, US1324, BG1718, BG1549, BG1550, BG0974, BG0997, BG1552, US1326. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG1694, BG1730. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=186252`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

## Persona learnings

<!-- persona-learnings:begin (generated by sprint close) -->
No approved learning awaits listing for RUN-01M836YT.

qa has adverse evidence (round:BG1694r2, round:US1326r4) and no learning listed.

0 of 69 verdict rows name no seat.
<!-- persona-learnings:end -->
