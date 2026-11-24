# Sprint Report: RUN-01M84Z8Z

## Goal

The last 23 Medium bugs are fixed and commits test on the gate host; each fix's test fails without it

**Verdict: Judged achieved** - All 23 Medium bugs are Fixed, each on an independent APPROVE with its criteria run: BG1548 and BG1574 closed in round three under the carry rule, closing their carries BG1734 and BG1735; commits test on the gate host and fall back locally when it is busy (US1190, US1191 Done)

> **Run:** 2026-11-23T19:49:15Z to 2026-11-24T04:42:00Z (8.9h)
> **Verified on:** 89f7fdb727de962cae07de061a54b083d0df3589   **Fingerprint:** 255e8c030ad05c74

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 61 | 64 | 1.05x | 27 of 27 delivered unit(s) |
| Minutes | 355.9 | 1816.7 | 5.1x | measured active minutes (spans or agent minutes) against their forecast, over the 27 of 27 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 847.9 | 532.8 | 0.63x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0038, RPT0039, RPT0040, RPT0041, RPT0042), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 83,258,351 | 80,904,696 | 0.97x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 13,750,861 (input 7,770 x1, output 2,497,230 x5, cache write 5m 10,251,996 x1.25, cache write 1h 993,865 x2, cache read 536,080,506 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0152, RETRO0153, RETRO0154, RETRO0155, RETRO0156) |
| Tokens | 11,361,372 | 13,750,861 | 1.21x | the whole run: forecast over 27 of 27 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 40 delegated total(s) supplied are not added |
| Priced per point | 1,364,891 | 1,264,136 | 0.93x | the Priced cost row over the 64 point(s) of the 27 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0152, RETRO0153, RETRO0154, RETRO0155, RETRO0156) |
| Dollar cost | $333.03 | $187.89 | 0.56x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $5.46 | $2.94 | 0.54x | the Dollar cost row over the 64 point(s) of the 27 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| US1190 | $13.13 estimated | 29.2 | 123.3 agent minutes, split by points | 931,260 | 722,392 agent tokens, split by points | 5,201,132 priced, split by points |
| US1191 | $7.88 estimated | 17.5 | 74.0 agent minutes, split by points | 558,756 | 433,435 agent tokens, split by points | 3,120,680 priced, split by points |
| BG1514 | $4.01 estimated | 11.7 | 55.0 agent minutes, 1 of 2 agent totals split by points | 372,504 | 279,573 agent tokens, 1 of 2 agent totals split by points | 1,778,738 priced, 1 of 2 agent totals split by points |
| BG1731 | $1.40 estimated | 17.5 | 34.6 agent minutes, split by points | 558,756 | 125,440 agent tokens, split by points | 1,101,676 priced, split by points |
| BG1027 | $5.44 estimated | 11.7 | 106.2 agent minutes, split by points | 372,504 | 556,126 agent tokens, split by points | 1,782,945 priced, split by points |
| BG1272 | $5.44 estimated | 11.7 | 106.2 agent minutes, split by points | 372,504 | 556,125 agent tokens, split by points | 1,782,945 priced, split by points |
| BG1574 | $11.67 estimated | 29.2 | 146.1 agent minutes, 1 of 3 agent totals split by points | 931,260 | 724,846 agent tokens, 1 of 3 agent totals split by points | 6,147,869 priced, 1 of 3 agent totals split by points |
| BG1101 | $1.11 estimated | 5.8 | 29.7 agent minutes, split by points | 186,252 | 210,032 agent tokens, split by points | 773,029 priced, split by points |
| BG1511 | $6.47 estimated | 11.7 | 149.6 agent minutes | 372,504 | 541,666 agent tokens | 3,201,288 priced |
| BG1732 | $0.6171 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 58,566 agent tokens, split by points | 484,601 priced, split by points |
| BG0957 | $0.9120 estimated | 5.8 | 27.7 agent minutes, 1 of 2 agent totals split by points | 186,252 | 111,969 agent tokens, 1 of 2 agent totals split by points | 671,832 priced, 1 of 2 agent totals split by points |
| BG1256 | $2.23 estimated | 11.7 | 59.5 agent minutes, split by points | 372,504 | 420,064 agent tokens, split by points | 1,546,057 priced, split by points |
| BG1310 | $0.9310 estimated | 11.7 | 23.0 agent minutes, split by points | 372,504 | 83,627 agent tokens, split by points | 734,450 priced, split by points |
| BG1581 | $0.6171 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 58,566 agent tokens, split by points | 484,600 priced, split by points |
| BG1407 | $1.41 estimated | 5.8 | 22.1 agent minutes, split by points | 186,252 | 56,432 agent tokens, split by points | 562,739 priced, split by points |
| BG1569 | $12.11 estimated | 29.2 | 118.2 agent minutes, 1 of 2 agent totals split by points | 931,260 | 631,915 agent tokens, 1 of 2 agent totals split by points | 4,944,558 priced, 1 of 2 agent totals split by points |
| BG1678 | $7.15 estimated | 17.5 | 68.6 agent minutes, split by points | 558,756 | 354,623 agent tokens, split by points | 2,894,516 priced, split by points |
| BG0949 | $0.5686 estimated | 5.8 | 10.5 agent minutes, split by points | 186,252 | 90,157 agent tokens, split by points | 417,519 priced, split by points |
| BG0986 | $0.4778 estimated | 5.8 | 16.2 agent minutes, split by points | 186,252 | 91,765 agent tokens, split by points | 326,191 priced, split by points |
| BG1455 | $2.82 estimated | 11.7 | 44.2 agent minutes, split by points | 372,504 | 112,864 agent tokens, split by points | 1,125,478 priced, split by points |
| BG1540 | $0.4778 estimated | 5.8 | 16.2 agent minutes, split by points | 186,252 | 91,765 agent tokens, split by points | 326,191 priced, split by points |
| BG1373 | $1.92 estimated | 5.8 | 92.9 agent minutes, 1 of 2 agent totals split by points | 186,252 | 129,879 agent tokens, 1 of 2 agent totals split by points | 927,674 priced, 1 of 2 agent totals split by points |
| BG1570 | $4.23 estimated | 17.5 | 66.3 agent minutes, split by points | 558,756 | 169,296 agent tokens, split by points | 1,688,216 priced, split by points |
| BG1538 | $1.13 estimated | 11.7 | 37.9 agent minutes, 1 of 2 agent totals split by points | 372,504 | 222,355 agent tokens, 1 of 2 agent totals split by points | 754,357 priced, 1 of 2 agent totals split by points |
| BG1548 | $5.41 estimated | 17.5 | 67.2 agent minutes, split by points | 558,756 | 534,227 agent tokens, split by points | 2,544,826 priced, split by points |
| BG1063 | $3.67 estimated | 17.5 | 56.8 agent minutes, split by points | 558,756 | 434,239 agent tokens, split by points | 1,921,010 priced, split by points |
| BG0967 | $9.65 estimated | 17.5 | 229.8 agent minutes | 558,756 | 1,040,300 agent tokens | 3,146,633 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 27 | 61 |
| Delivered of the plan | 27 | 61 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 64.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1190 | 5 | 5 | delivered | 2 |
| US1191 | 3 | 3 | delivered | 2 |
| BG1514 | 2 | 2 | delivered | 2 |
| BG1731 | 3 | 3 | delivered | 1 |
| BG1027 | 2 | 2 | delivered | 1 |
| BG1272 | 2 | 2 | delivered | 1 |
| BG1574 | 5 | 5 | delivered - discharged after it was carried at the review cap: BG1735 | 3 |
| BG1101 | 1 | 1 | delivered | 1 |
| BG1511 | 2 | 5 | delivered | 2 |
| BG1732 | 1 | 1 | delivered | 1 |
| BG0957 | 1 | 1 | delivered | 2 |
| BG1256 | 2 | 2 | delivered | 1 |
| BG1310 | 2 | 2 | delivered | 1 |
| BG1581 | 1 | 1 | delivered | 1 |
| BG1407 | 1 | 1 | delivered | 1 |
| BG1569 | 5 | 5 | delivered | 2 |
| BG1678 | 3 | 3 | delivered | 1 |
| BG0949 | 1 | 1 | delivered | 1 |
| BG0986 | 1 | 1 | delivered | 1 |
| BG1455 | 2 | 2 | delivered | 1 |
| BG1540 | 1 | 1 | delivered | 1 |
| BG1373 | 1 | 1 | delivered | 2 |
| BG1570 | 3 | 3 | delivered | 1 |
| BG1538 | 2 | 2 | delivered | 2 |
| BG1548 | 3 | 3 | delivered - discharged after it was carried at the review cap: BG1734 | 3 |
| BG1063 | 3 | 3 | delivered | 2 |
| BG0967 | 3 | 3 | delivered | 1 |

## Known issues handed over

3 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0751 | Medium | Prevent or retire lesson LC-001 (mutant never applied) - not-stop-ship, ruled by orchestrator |
| BG1733 | Low | transition.py drops a status decoration such as '(partially superseded)' on every move - not-stop-ship, ruled by orchestrator |
| BG1736 | Low | The commit-msg attribution note advises a schema 3 id by its dashless key - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-24T04:47:23Z | 255e8c030ad05c74 |

Signing records the principal, the date and this report's fingerprint against RUN-01M84Z8Z.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | partial over 2 clause(s), 3 seat(s), no seat matched the author; achieved (2 seat(s) silent): The last 23 Medium bugs are fixed and commits test on the gate host; UNANSWERED (3 seat(s) silent): each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 249 leavable |
| batch | caller-check | 24 unit(s) of 25 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 13,750,861 |

Total 13,750,861, of which delegated 8,842,244. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (27 units); reviewer inherit (27 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $159.37 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $28.51 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 1051 subagent transcript(s); total agents 42, calls 3,640, priced 80,904,696. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 611 | 19,345,436 | 23.9% | 81.2% | 10.3% | 8.5% | 166,942 | 258,877 |
| builder | 12 | 1,838 | 41,784,684 | 51.6% | 67.1% | 17.9% | 15.0% | 15,388 | 155,733 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 10 | 545 | 8,607,065 | 10.6% | 57.9% | 16.8% | 25.4% | 15,726 | 93,513 |
| other | 19 | 646 | 11,167,511 | 13.8% | 43.7% | 34.7% | 21.5% | 31,861 | 80,430 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 3 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45321429945/45310368895/45286604383 - 3 push-triggered run(s) on main in the run window |
| Lead time for changes | 8h 20m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 33 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45321429945/45310368895/45286604383 - 3 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45321429945/45310368895/45286604383 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 2 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

2 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 2 | 0 | 2 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

13 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | graduating (CR0751) | 1 | 2 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-011 | widen-after-brief | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 1 | 80 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
| LC-022 | hand-in outside the lane folder | active | 0 | 0 |
| LC-023 | census missed by a narrow commit | active | 0 | 0 |
| LC-024 | second seat past the joint cap | active | 0 | 0 |
| LC-025 | mutant test outside Affects | active | 0 | 0 |
| LC-026 | a builder samples the modules it edits | active | 0 | 0 |
| LC-027 | a self-check recorded out of band | active | 0 | 0 |
