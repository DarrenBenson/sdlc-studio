# Sprint Report: RUN-01M7GEHM

## Goal

A head of engineering evaluates, tries or upgrades from the README and reads each run's evidence and cost

**Verdict: Judged achieved** - A head of engineering can now evaluate, try or upgrade from a README that opens with those three routes, read the signed reports of record as one generated evidence page, see what support exists and how change approval and cost work, and read the reasoning effort each builder and reviewer ran at on the run's report. US1168 was dropped under D0495 for a regroom; six in-run fixes include BG1489, which turned GitHub CI green again.

> **Run:** 2026-11-15T20:23:48Z to 2026-11-16T04:08:57Z (7.8h)
> **Verified on:** 7e3615c02c812f2abcd013d02104766aa10b411e   **Fingerprint:** 47fd8b167ed17112

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 50 | 50 | 1.0x | 21 of 21 delivered unit(s) |
| Minutes | 286.1 | 2128.7 | 7.44x | measured active minutes (spans or agent minutes) against their forecast, over the 20 of 21 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 391.9 | 465.1 | 1.19x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0028, RPT0029, RPT0030, RPT0031, RPT0032), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 42,277,100 | 39,710,601 | 0.94x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 6,423,229 (input 4,280 x1, output 1,670,591 x5, cache write 5m 4,211,526 x1.25, cache write 1h 536,832 x2, cache read 250,152,946 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0142, RETRO0143, RETRO0144, RETRO0145, RETRO0146) |
| Tokens | 9,312,600 | 6,423,229 | 0.69x | the whole run: forecast over 21 of 21 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 24 delegated total(s) supplied are not added |
| Priced per point | 845,542 | 794,212 | 0.94x | the Priced cost row over the 50 point(s) of the 21 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0142, RETRO0143, RETRO0144, RETRO0145, RETRO0146) |
| Dollar cost | $169.11 | $108.81 | 0.64x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.38 | $2.18 | 0.64x | the Dollar cost row over the 50 point(s) of the 21 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0947 | $1.50 estimated | 11.7 | 111.4 | 372,504 | 82,605 agent tokens, split by points | 533,733 priced, split by points |
| BG0998 | $3.07 estimated | 11.7 | 94.4 | 372,504 | 206,366 agent tokens, split by points | 1,129,240 priced, split by points |
| BG1260 | $1.54 estimated | 11.7 | 93.7 | 372,504 | 95,030 agent tokens, split by points | 542,529 priced, split by points |
| BG1395 | $1.64 estimated | 11.7 | 72.6 | 372,504 | 110,669 agent tokens, split by points | 545,779 priced, split by points |
| BG1396 | $1.64 estimated | 11.7 | 74.2 | 372,504 | 110,670 agent tokens, split by points | 545,779 priced, split by points |
| US1160 | $5.10 estimated | 17.5 | 129.1 | 558,756 | 359,755 agent tokens, 1 of 2 agent totals split by points | 1,793,228 priced, 1 of 2 agent totals split by points |
| US1161 | $2.58 estimated | 11.7 | 97.8 | 372,504 | 180,764 agent tokens, split by points | 918,198 priced, split by points |
| US1162 | $2.39 estimated | 17.5 | 73.1 | 558,756 | 139,877 agent tokens, split by points | 846,349 priced, split by points |
| US1163 | $1.60 estimated | 11.7 | 73.3 | 372,504 | 93,251 agent tokens, split by points | 564,232 priced, split by points |
| US1165 | $2.32 estimated | 17.5 | 93.2 | 558,756 | 142,546 agent tokens, split by points | 813,793 priced, split by points |
| US1166 | $4.61 estimated | 17.5 | 94.0 | 558,756 | 309,549 agent tokens, split by points | 1,693,859 priced, split by points |
| US1167 | $8.26 estimated | 17.5 | 313.1 | 558,756 | 445,033 agent tokens | 3,030,959 priced |
| US1169 | $5.98 estimated | 29.2 | 146.4 | 931,260 | 349,744 agent tokens, 1 of 2 agent totals split by points | 2,092,256 priced, 1 of 2 agent totals split by points |
| BG1177 | $0.7960 estimated | 5.8 | 95.5 | 186,252 | 45,206 agent tokens, split by points | 285,560 priced, split by points |
| US1164 | $3.98 estimated | 29.2 | 95.7 | 931,260 | 226,027 agent tokens, split by points | 1,427,800 priced, split by points |
| BG1474 | $1.95 estimated | 11.7 | 62.6 | 372,504 | 129,555 agent tokens | 669,261 priced |
| BG1478 | $0.8323 estimated | 5.8 | 88.1 | 186,252 | 46,058 agent tokens, split by points | 299,908 priced, split by points |
| BG1479 | $2.50 estimated | 17.5 | 93.0 | 558,756 | 138,175 agent tokens, split by points | 899,724 priced, split by points |
| BG1480 | $0.8323 estimated | 5.8 | 89.2 | 186,252 | 46,058 agent tokens, split by points | 299,908 priced, split by points |
| BG1484 | $0.8322 estimated | 5.8 | NOT MEASURED - 0 of its 1 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 186,252 | 46,058 agent tokens, split by points | 299,908 priced, split by points |
| BG1489 | $2.98 estimated | 11.7 | 138.2 | 372,504 | 252,055 agent tokens | 1,000,283 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 16 | 42 |
| Delivered of the plan | 15 | 40 |
| Added mid-run and delivered | 6 of 6 added | 10 |
| Dropped | 1 | 2 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 50.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0947 | 2 | 2 | delivered | 1 |
| BG0998 | 2 | 2 | delivered | 1 |
| BG1260 | 2 | 2 | delivered | 1 |
| BG1395 | 2 | 2 | delivered | 1 |
| BG1396 | 2 | 2 | delivered | 1 |
| US1160 | 3 | 3 | delivered | 2 |
| US1161 | 2 | 2 | delivered | 1 |
| US1162 | 3 | 3 | delivered | 1 |
| US1163 | 2 | 2 | delivered | 1 |
| US1165 | 3 | 3 | delivered | 1 |
| US1166 | 3 | 3 | delivered | 1 |
| US1167 | 3 | 3 | delivered | 2 |
| US1168 | 2 | 2 | dropped - D0495: needs a new script and a ruled commit-lane cap change; regroom for a later run | 0 |
| US1169 | 5 | 5 | delivered | 2 |
| BG1177 | 1 | 1 | delivered | 1 |
| US1164 | 5 | 5 | delivered | 1 |
| BG1474 | 2 | 2 | added - D0490: the push boundary refused run thirteen's seal over the retired build-trap classes; delivered | 1 |
| BG1478 | 1 | 1 | added - D0491: the front door's support policy names an old major as current; delivered | 1 |
| BG1479 | 3 | 3 | added - D0492: QA review findings on wave 1's pages and fragments; delivered | 1 |
| BG1480 | 1 | 1 | added - D0492: QA review findings on wave 1's pages and fragments; delivered | 1 |
| BG1484 | 1 | 1 | added - D0493: the push boundary refused 46db0430 on test_quiet_success; delivered | 1 |
| BG1489 | 2 | 2 | added - D0494: GitHub Lint red on main, noise gate 112 over 104; delivered | 1 |

## Known issues handed over

18 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1493 | High | The pre-push boundary gate does not run CI's green-run noise gate, so a push that passes locally turns GitHub Lint red - not-stop-ship, ruled by orchestrator |
| BG1475 | Medium | sprint close --dry-run takes about half an hour and prints nothing until it ends, mostly one git log per artefact in the review-current check - not-stop-ship, ruled by orchestrator |
| BG1477 | Medium | lane accept --agent on a multi-unit lane charges the builder's whole transcript to each unit, overriding the land's split by points - not-stop-ship, ruled by orchestrator |
| BG1482 | Medium | A build-injected lesson class can no longer retire, so once more than INJECT_MAX build classes are live the digest cap drops the oldest builder traps - not-stop-ship, ruled by orchestrator |
| BG1483 | Medium | A run's repeat of a lesson class is counted only from a cited REJECT or retro Try item, so a repeat caught by the land or the push gate goes unrecorded - not-stop-ship, ruled by orchestrator |
| BG1487 | Medium | The README's opening says a person you can name reviews and approves each step, and it no longer points agents at llms.txt or AGENTS.md - not-stop-ship, ruled by orchestrator |
| BG1491 | Medium | lane accept on an APPROVE prints that the unit moved to Fixed and then that its return is blocked, when one criterion has no Verify line - not-stop-ship, ruled by orchestrator |
| BG1492 | Medium | Nothing stops the orchestrator committing a reviewer's half-written verdict: git add of the records sweeps in a verdict file still being written - not-stop-ship, ruled by orchestrator |
| CR0710 | Medium | CR0699 remainder: the bench runner takes a builder-effort arm and reports priced tokens per point, review rounds and the held-back score per arm - not-stop-ship, ruled by orchestrator |
| CR0711 | Medium | Show each open lane's liveness, so a stalled builder is caught in minutes rather than hours - not-stop-ship, ruled by orchestrator |
| CR0712 | Medium | Prevent or retire lesson LC-010 (the push gate and CI disagree on the runner) - not-stop-ship, ruled by orchestrator |
| BG1476 | Low | file_finding stamps Raised-in-batch as none open for a finding filed while a run is open - not-stop-ship, ruled by orchestrator |
| BG1481 | Low | test_support_page lets four planted SUPPORT.md defects through: a gh skills install line, an install command in prose, and Stack Overflow or IRC named in prose - not-stop-ship, ruled by orchestrator |
| BG1485 | Low | A shell Verify line run with -s still reads all-skipped and no-tests shapes from its whole output, and a partial-skip test's docstring still says the release gate counts the skips - not-stop-ship, ruled by orchestrator |
| BG1486 | Low | US1157's AC1 names a file_finding.py bug verb that does not exist, so the plan's registry advice reads it as a new verb - not-stop-ship, ruled by orchestrator |
| BG1488 | Low | reference-outputs.md still calls Deferred a story terminal status at lines 134, 745 and 755, against its own Story row and sdlc_md.TERMINAL_STATUS - not-stop-ship, ruled by orchestrator |
| BG1490 | Low | test_critic_rejoinder_from_ledger and test_critic_verdict_file_binding fail when run inside an agent session, because the harness session id reaches the verdict's source field - not-stop-ship, ruled by orchestrator |
| CR0709 | Low | Add lessons.py reinstate: put a retired class back in force with a recorded run and reason - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-16T04:12:46Z | 47fd8b167ed17112 |

Signing records the principal, the date and this report's fingerprint against RUN-01M7GEHM.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 6,423,229 |

Total 6,423,229, of which delegated 3,555,051. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder NOT MEASURED - the plan this run was opened from stamped no effort on its units: it was planned before the effort setting existed; reviewer NOT MEASURED - the plan this run was opened from stamped no effort on its units: it was planned before the effort setting existed.

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $108.81 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 613 subagent transcript(s); total agents 27, calls 2,067, priced 39,710,601. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 369 | 10,909,133 | 27.5% | 82.0% | 9.8% | 8.2% | 330,186 | 243,866 |
| builder | 11 | 1,007 | 18,411,330 | 46.4% | 60.0% | 15.5% | 24.5% | 14,009 | 111,960 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 3 | 149 | 1,820,955 | 4.6% | 52.6% | 17.8% | 29.6% | 13,598 | 66,064 |
| other | 12 | 542 | 8,569,183 | 21.6% | 47.5% | 24.3% | 28.2% | 13,678 | 78,103 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 43796936774/43772359267 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 7h 9m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 35 commit(s) |
| Change failure rate | 100% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 43796936774/43772359267 - 2 deployment(s); 2 failed on 1e2c04459300bc9e19e44641963bcdcd24c4513c/7c64bf26c7fd486720da069b17dd6f1ef7a4c18f |
| Time to restore | not restored | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 43772359267 - main went red at run 43772359267, and no push-triggered run created after it concluded success in the run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

2 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 2 | 0 | 2 | delete candidate: 8 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 1 | 2 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 37 |
| LC-019 | a push-gate guard the per-commit run skips | active | 1 | 1 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 1 | 1 |
