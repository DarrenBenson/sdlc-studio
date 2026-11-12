# Sprint Report: RUN-01M77177

## Goal

A signed report's verdicts are provably the reviewers' own, and the report is reviewable from the committed tree.

**Verdict: Judged achieved** - All 18 units delivered on independent APPROVEs (57 points): every EP0280 story binds a recorded verdict to the file its brief issued, names the agent that wrote it and records an editing context as a self-review; EP0276 cites the committed run record, names the plan by digest, freezes prices and the lane-yield tally. Reopened once (D0468) to fix BG1374, the report twin's bare price-source URL. US0999 was deferred to run eleven (D0465), and this run's own record still names its plan by the .local path because it opened before US0998.

> **Run:** 2026-11-12T04:52:40Z to 2026-11-12T14:30:11Z (9.6h)
> **Verified on:** 6d997ebfdbfd47a9f9e4bcab73ac97bb3639d736   **Fingerprint:** 92ed4ae3b01b2bf2

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 57 | 57 | 1.0x | 18 of 18 delivered unit(s) |
| Minutes | 315.2 | 1539.4 | 4.88x | measured active minutes (spans or agent minutes) against their forecast, over the 17 of 18 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 577.5 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 45,104,920 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 8,290,038 (input 4,250 x1, output 1,939,529 x5, cache write 5m 5,539,932 x1.25, cache write 1h 806,327 x2, cache read 268,654,564 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 10,616,364 | 8,290,038 | 0.78x | the whole run: forecast over 18 of 18 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 20 delegated total(s) supplied are not added |
| Priced per point | not forecast | 791,314 | no ratio | the Priced cost row over the 57 point(s) of the 18 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast | $126.37 | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-09; covers 100.0% of the priced tokens |
| Dollars per point | not forecast | $2.22 | no ratio | the Dollar cost row over the 57 point(s) of the 18 delivered unit(s); price table effective 2026-11-09 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1300 | $1.38 estimated | 11.7 | 503.8 | 372,504 | 108,154 agent tokens | 438,467 priced |
| US0997 | $3.58 estimated | 17.5 | 41.4 | 558,756 | 297,112 agent tokens | 1,195,673 priced |
| US0998 | $2.81 estimated | 11.7 | 60.4 | 372,504 | 173,528 agent tokens | 978,870 priced |
| US1000 | $5.30 estimated | 29.2 | 120.0 | 931,260 | 335,552 agent tokens | 1,862,467 priced |
| US1134 | $4.48 estimated | 29.2 | 61.3 | 931,260 | 267,459 agent tokens | 1,597,328 priced |
| US1147 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1147 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1147 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1147 --agent A` |
| US1149 | $7.45 estimated | 29.2 | 103.1 | 931,260 | 539,333 agent tokens | 2,602,031 priced |
| BG1010 | $2.02 estimated | 5.8 | 50.9 | 186,252 | 161,753 agent tokens | 637,146 priced |
| US1001 | $2.66 estimated | 17.5 | 104.9 | 558,756 | 176,917 agent tokens | 903,647 priced |
| BG1030 | $2.50 estimated | 17.5 | 27.0 | 558,756 | 170,731 agent tokens | 841,044 priced |
| US1011 | $3.47 estimated | 11.7 | 63.8 | 372,504 | 296,019 agent tokens | 1,117,361 priced |
| US1012 | $6.68 estimated | 29.2 | 49.9 | 931,260 | 460,555 agent tokens | 2,415,641 priced |
| US1013 | $4.09 estimated | 17.5 | 51.0 | 558,756 | 258,233 agent tokens | 1,375,707 priced |
| US1014 | $3.77 estimated | 29.2 | 116.1 | 931,260 | 229,283 agent tokens | 1,284,243 priced |
| US1015 | $3.13 estimated | 29.2 | 35.8 | 931,260 | 204,770 agent tokens | 1,045,730 priced |
| US1016 | $5.89 estimated | 17.5 | 79.7 | 558,756 | 638,872 agent tokens | 1,875,735 priced |
| BG1334 | $0.8336 estimated | 5.8 | 54.8 | 186,252 | 66,080 agent tokens | 262,225 priced |
| BG1374 | $1.45 estimated | 5.8 | 15.6 | 186,252 | 112,873 agent tokens | 459,344 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 16 | 55 |
| Delivered of the plan | 16 | 55 |
| Added mid-run and delivered | 2 of 2 added | 2 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 57.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1300 | 2 | 2 | delivered | 1 |
| US0997 | 3 | 3 | delivered | 1 |
| US0998 | 2 | 2 | delivered | 1 |
| US1000 | 5 | 5 | delivered | 2 |
| US1134 | 5 | 5 | delivered | 1 |
| US1147 | 3 | 3 | delivered | 1 |
| US1149 | 5 | 5 | delivered | 2 |
| BG1010 | 1 | 1 | delivered | 2 |
| US1001 | 3 | 3 | delivered | 1 |
| BG1030 | 3 | 3 | delivered | 1 |
| US1011 | 2 | 2 | delivered | 1 |
| US1012 | 5 | 5 | delivered | 1 |
| US1013 | 3 | 3 | delivered | 1 |
| US1014 | 5 | 5 | delivered | 1 |
| US1015 | 5 | 5 | delivered | 1 |
| US1016 | 3 | 3 | delivered | 1 |
| BG1334 | 1 | 1 | added - US1011's verdict files under sdlc-studio/reviews/verdicts/ turned main red at test_verify_ac's markdown-evidence lint; it blocks US1000's land and the push gate, so it is fixed in-run; delivered | 1 |
| BG1374 | 1 | 1 | added - RPT0029 fails markdownlint MD034 because US1000's Prices table prints the price source URL bare; the close paperwork cannot be committed, so it is fixed in-run after the reopen (D0468); delivered | 1 |

## Known issues handed over

46 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1336 | Medium | The lane brief's verify_ac step writes into the unit's own artefact outside its Affects, and lane land's rebase then fails on that unstaged edit while exiting 0 under a pipe - not-stop-ship, ruled by orchestrator |
| BG1337 | Medium | sprint.py lane land commits a lane at its worktree's old base and rebases afterwards, so the hook judges it against code main has already fixed - not-stop-ship, ruled by orchestrator |
| BG1339 | Medium | sprint.py lane accept has no path for a round-2 verdict given against a rejoinder brief, so the orchestrator records it by hand - not-stop-ship, ruled by orchestrator |
| BG1340 | Medium | critic.py brief --rejoinder with no file reads only the unit's current delivery, so a unit carried across runs has no ledger rejoinder - not-stop-ship, ruled by orchestrator |
| BG1341 | Medium | reconcile.blocking_findings lists a REJECT row's RULINGS item as a blocking defect in a lane brief's file history - not-stop-ship, ruled by orchestrator |
| BG1343 | Medium | Moving a story to Ready does not refuse a criterion with several stacked Verify lines, which then turns main red at StackedVerifierTests - not-stop-ship, ruled by orchestrator |
| BG1344 | Medium | A unit whose tests must run under a temporary HOME cannot be built in a worktree lane, and the lane brief offers no other path - not-stop-ship, ruled by orchestrator |
| BG1371 | Medium | The retro's dollar line prices only the meter's split, so the retro and the report state different dollars for one run - not-stop-ship, ruled by orchestrator |
| BG1372 | Medium | GitHub reports 5 Dependabot alerts on the default branch (1 high, 2 moderate, 2 low) - not-stop-ship, ruled by orchestrator |
| BG1373 | Medium | A NUL byte in a transcript's file path makes critic.py record refuse the unit - not-stop-ship, ruled by orchestrator |
| BG1335 | Low | sprint.py decision defer --block cannot mark a bug Blocked, so an autonomous run's blocked bug reads as an ordinary open unit - not-stop-ship, ruled by orchestrator |
| BG1338 | Low | The lane brief does not tell a builder to fast-forward its worktree, and harness worktrees start at origin's commit, so builders build on a base missing the run's landed units - not-stop-ship, ruled by orchestrator |
| BG1342 | Low | sprint.py plan --write --format json prints its run-opening lines on stdout before the JSON - not-stop-ship, ruled by orchestrator |
| BG1345 | Low | The review brief does not tell a reviewer to keep tools that write under the home directory, such as npx and npm, out of its probes - not-stop-ship, ruled by orchestrator |
| BG1346 | Low | The first verdict recorded after the ledger gained its Source column pads every row, and the commit-msg hook credits that change to every unit the subject names - not-stop-ship, ruled by orchestrator |
| BG1347 | Low | A second RULINGS: line in a verdict block is silently dropped - not-stop-ship, ruled by orchestrator |
| BG1348 | Low | critic.py's 'none blocking' guard has no test - not-stop-ship, ruled by orchestrator |
| BG1349 | Low | No test pins that a verdict file stays under --root inside a larger git repository - not-stop-ship, ruled by orchestrator |
| BG1350 | Low | sprint_report._cited_record's run-archive branch has no test - not-stop-ship, ruled by orchestrator |
| BG1351 | Low | US1149's tests have no fixture with two synthetic records in a row - not-stop-ship, ruled by orchestrator |
| BG1352 | Low | US1013's in-order comparison of a verdict and its issued file has no pinning test - not-stop-ship, ruled by orchestrator |
| BG1353 | Low | Two branches of US1016's rejoinder selection have no test - not-stop-ship, ruled by orchestrator |
| BG1354 | Low | The close's re-close window_end wiring has no test - not-stop-ship, ruled by orchestrator |
| BG1355 | Low | Four branches US1014's claims name have no test - not-stop-ship, ruled by orchestrator |
| BG1356 | Low | US1000's AC2 test holds one read record per model, so replacing components across records survives - not-stop-ship, ruled by orchestrator |
| BG1357 | Low | The report's Prices NOT MEASURED reasons and _run_usd's no-split guard are unpinned - not-stop-ship, ruled by orchestrator |
| BG1358 | Low | US0997's changelog and reference-scripts.md say the close commits the run record, but it files it - not-stop-ship, ruled by orchestrator |
| BG1359 | Low | help/sprint.md says the run record never names the plan by its .local path, but a run opened before 509850a1 still does - not-stop-ship, ruled by orchestrator |
| BG1360 | Low | reference-scripts-review.md says row_identity digests the first eight cells, but in a nine-cell row it digests every cell except Source - not-stop-ship, ruled by orchestrator |
| BG1361 | Low | US1001's note says 'this clone's refusal log', which misleads in a fresh clone - not-stop-ship, ruled by orchestrator |
| BG1362 | Low | BG1334's changelog and docstring claim more than the path-as-written match - not-stop-ship, ruled by orchestrator |
| BG1363 | Low | The US1000 report's price rows cite the config while their values come from the page's own price table - not-stop-ship, ruled by orchestrator |
| BG1364 | Low | fresh_session: no or false reads as off, though the help and US1149's AC2 say any other value reads as warn - not-stop-ship, ruled by orchestrator |
| BG1365 | Low | sprint_report.py build of a signed run ignores the time window saved on its signed page - not-stop-ship, ruled by orchestrator |
| BG1366 | Low | The verdict-file header check misses a byte order mark, a lower-case header or a leading prose line - not-stop-ship, ruled by orchestrator |
| BG1367 | Low | The replay refusal tells a lane accept retry to re-brief when only the verify and the move are owed - not-stop-ship, ruled by orchestrator |
| BG1368 | Low | After the rejecting reviewer's round-2 APPROVE, rebrief_notice names a bare --rejoinder that exits 2 - not-stop-ship, ruled by orchestrator |
| BG1369 | Low | verify_ac's markdown-evidence lint matches the verdicts path as written, so reviews/../reviews/ and a symlink get through - not-stop-ship, ruled by orchestrator |
| BG1370 | Low | A later rewrite of a verdict file is attributed to the reviewer when its last write was an Edit - not-stop-ship, ruled by orchestrator |
| BG1375 | Low | US1015's run-state floor and its Write, MultiEdit, NotebookEdit, Read and Bash evidence cases have no tests - not-stop-ship, ruled by orchestrator |
| BG1376 | Low | US1015's brief bound counts any round's issued path, not the round being recorded - not-stop-ship, ruled by orchestrator |
| BG1377 | Low | The hooks' replay of a refusal's stderr is not pinned - not-stop-ship, ruled by orchestrator |
| BG1378 | Low | US1134's AC3 skips markdownlint without saying so when the binary is missing - not-stop-ship, ruled by orchestrator |
| BG1379 | Low | The report's Markdown twin still prints a `www.` or upper-case-scheme price source bare - not-stop-ship, ruled by orchestrator |
| BG1380 | Low | BG1374's exclusion of a trailing comma or full stop from a linked address has no test - not-stop-ship, ruled by orchestrator |
| BG1381 | Low | A price source URL whose path ends in a closing bracket loses that bracket from its link target - not-stop-ship, ruled by orchestrator |
| checklist | close gap | tick-verification: Ticked criteria the tree supports - 7 ticked criterion/criteria unsupported |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M77177.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 8,290,038 |

Total 8,290,038, of which delegated 4,497,224. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-haiku-5-5 | $0.10 | $0.50 | $0.125 | $0.20 | $0.01 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $0.0087 |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $126.36 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 487 subagent transcript(s); total agents 39, calls 2,033, priced 45,104,920. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 304 | 14,817,164 | 32.9% | 82.8% | 10.9% | 6.4% | 227,263 | 406,038 |
| builder | 16 | 1,086 | 19,457,965 | 43.1% | 53.5% | 20.0% | 26.5% | 13,531 | 98,786 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 3 | 97 | 975,349 | 2.2% | 44.6% | 23.1% | 32.3% | 13,762 | 46,664 |
| other | 19 | 546 | 9,854,443 | 21.8% | 38.1% | 28.6% | 33.4% | 13,894 | 72,822 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 43212604439/43190396246 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 11h 49m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 34 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 43212604439/43190396246 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 43212604439/43190396246 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 3 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 4 | 0 | 4 | delete candidate: 8 refusal(s) over 3 runs and no candidate catch |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | graduating (CR0684) | 0 | 3 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 0 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 0 | 30 |
| LC-019 | a push-gate guard the per-commit run skips | active | 0 | 0 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 0 |
