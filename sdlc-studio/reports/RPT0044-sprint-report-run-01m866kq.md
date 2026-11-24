# Sprint Report: RUN-01M866KQ

## Goal

The eighteen Lows the operator kept are fixed with fourteen more from their files; each fix's test fails without it

**Verdict: Judged achieved** - All 32 units Fixed on independent APPROVEs: the 18 operator-kept Lows plus 14 from their files; each review ran the unit's new tests against base and saw them fail, and BG1204 closed through its carry exit in round six.

> **Run:** 2026-11-24T07:15:07Z to 2026-11-24T16:46:35Z (9.5h)
> **Verified on:** 08dfcdedc89e42dcdfc8aa76c7f29dd8ab9a2562   **Fingerprint:** c554d224c96c99c8

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 55 | 55 | 1.0x | 32 of 32 delivered unit(s) |
| Minutes | 320.7 | 772.1 | 2.41x | measured active minutes (spans or agent minutes) against their forecast, over the 32 of 32 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 764.5 | 571.5 | 0.75x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0039, RPT0040, RPT0041, RPT0042, RPT0043), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 75,069,005 | 61,893,973 | 0.82x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 12,716,525 (input 4,638 x1, output 1,853,956 x5, cache write 5m 10,425,419 x1.25, cache write 1h 432,512 x2, cache read 387,227,568 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0153, RETRO0154, RETRO0155, RETRO0156, RETRO0157) |
| Tokens | 10,243,860 | 12,716,525 | 1.24x | the whole run: forecast over 32 of 32 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 50 delegated total(s) supplied are not added |
| Priced per point | 1,364,891 | 1,125,345 | 0.82x | the Priced cost row over the 55 point(s) of the 32 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0153, RETRO0154, RETRO0155, RETRO0156, RETRO0157) |
| Dollar cost | $300.28 | $161.82 | 0.54x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $5.46 | $2.94 | 0.54x | the Dollar cost row over the 55 point(s) of the 32 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0975 | $2.70 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 203,989 agent tokens, split by points | 978,179 priced, split by points |
| BG0996 | $0.2740 estimated | 5.8 | 5.9 agent minutes, split by points | 186,252 | 37,852 agent tokens, split by points | 200,238 priced, split by points |
| BG1062 | $3.47 estimated | 11.7 | 21.0 agent minutes, split by points | 372,504 | 212,883 agent tokens, split by points | 1,315,942 priced, split by points |
| BG1069 | $1.74 estimated | 5.8 | 10.9 agent minutes, split by points | 186,252 | 134,704 agent tokens, split by points | 626,574 priced, split by points |
| BG1073 | $2.70 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 203,990 agent tokens, split by points | 978,180 priced, split by points |
| BG1121 | $8.10 estimated | 17.5 | 52.1 agent minutes, split by points | 558,756 | 611,969 agent tokens, split by points | 2,934,540 priced, split by points |
| BG1126 | $1.15 estimated | 5.8 | 6.9 agent minutes, split by points | 186,252 | 79,351 agent tokens, split by points | 426,588 priced, split by points |
| BG1131 | $0.7600 estimated | 11.7 | 10.0 agent minutes, split by points | 372,504 | 132,259 agent tokens, split by points | 540,849 priced, split by points |
| BG1204 | $17.83 estimated | 17.5 | 177.0 agent minutes, 3 of 4 agent totals split by points | 558,756 | 1,847,220 agent tokens, 3 of 4 agent totals split by points | 6,392,838 priced, 3 of 4 agent totals split by points |
| BG1219 | $0.2740 estimated | 5.8 | 5.9 agent minutes, split by points | 186,252 | 37,852 agent tokens, split by points | 200,238 priced, split by points |
| BG1311 | $5.20 estimated | 17.5 | 31.6 agent minutes, split by points | 558,756 | 319,325 agent tokens, split by points | 1,973,913 priced, split by points |
| BG1323 | $3.33 estimated | 17.5 | 52.3 agent minutes, split by points | 558,756 | 350,836 agent tokens, split by points | 1,446,546 priced, split by points |
| BG1361 | $0.3800 estimated | 5.8 | 5.0 agent minutes, split by points | 186,252 | 66,129 agent tokens, split by points | 270,424 priced, split by points |
| BG1398 | $1.15 estimated | 5.8 | 6.9 agent minutes, split by points | 186,252 | 79,351 agent tokens, split by points | 426,588 priced, split by points |
| BG1404 | $1.74 estimated | 5.8 | 10.9 agent minutes, split by points | 186,252 | 134,704 agent tokens, split by points | 626,575 priced, split by points |
| BG1429 | $0.7600 estimated | 11.7 | 10.0 agent minutes, split by points | 372,504 | 132,258 agent tokens, split by points | 540,849 priced, split by points |
| BG1450 | $1.74 estimated | 5.8 | 10.9 agent minutes, split by points | 186,252 | 134,704 agent tokens, split by points | 626,575 priced, split by points |
| BG1473 | $2.24 estimated | 11.7 | 21.2 agent minutes, split by points | 372,504 | 256,867 agent tokens, split by points | 1,062,168 priced, split by points |
| BG1513 | $5.20 estimated | 17.5 | 31.6 agent minutes, split by points | 558,756 | 319,325 agent tokens, split by points | 1,973,913 priced, split by points |
| BG1562 | $2.22 estimated | 11.7 | 34.9 agent minutes, split by points | 372,504 | 233,891 agent tokens, split by points | 964,363 priced, split by points |
| BG1564 | $0.5480 estimated | 11.7 | 11.9 agent minutes, split by points | 372,504 | 75,704 agent tokens, split by points | 400,475 priced, split by points |
| BG1583 | $2.30 estimated | 11.7 | 13.8 agent minutes, split by points | 372,504 | 158,703 agent tokens, split by points | 853,175 priced, split by points |
| BG1591 | $2.70 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 203,989 agent tokens, split by points | 978,179 priced, split by points |
| BG1598 | $2.24 estimated | 11.7 | 21.2 agent minutes, split by points | 372,504 | 256,866 agent tokens, split by points | 1,062,167 priced, split by points |
| BG1606 | $5.40 estimated | 11.7 | 34.7 agent minutes, split by points | 372,504 | 407,980 agent tokens, split by points | 1,956,359 priced, split by points |
| BG1608 | $1.15 estimated | 5.8 | 6.9 agent minutes, split by points | 186,252 | 79,351 agent tokens, split by points | 426,587 priced, split by points |
| BG1650 | $3.33 estimated | 17.5 | 52.3 agent minutes, split by points | 558,756 | 350,835 agent tokens, split by points | 1,446,545 priced, split by points |
| BG1658 | $1.15 estimated | 5.8 | 6.9 agent minutes, split by points | 186,252 | 79,351 agent tokens, split by points | 426,587 priced, split by points |
| BG1673 | $1.15 estimated | 5.8 | 6.9 agent minutes, split by points | 186,252 | 79,351 agent tokens, split by points | 426,587 priced, split by points |
| BG1692 | $3.47 estimated | 11.7 | 21.0 agent minutes, split by points | 372,504 | 212,883 agent tokens, split by points | 1,315,942 priced, split by points |
| BG1698 | $3.47 estimated | 11.7 | 21.8 agent minutes, split by points | 372,504 | 269,409 agent tokens, split by points | 1,253,149 priced, split by points |
| BG1736 | $1.11 estimated | 5.8 | 17.4 agent minutes, split by points | 186,252 | 116,945 agent tokens, split by points | 482,182 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 32 | 55 |
| Delivered of the plan | 32 | 55 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 55.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0975 | 1 | 1 | delivered | 2 |
| BG0996 | 1 | 1 | delivered | 1 |
| BG1062 | 2 | 2 | delivered | 2 |
| BG1069 | 1 | 1 | delivered | 1 |
| BG1073 | 1 | 1 | delivered | 2 |
| BG1121 | 3 | 3 | delivered | 2 |
| BG1126 | 1 | 1 | delivered | 1 |
| BG1131 | 2 | 2 | delivered | 1 |
| BG1204 | 3 | 3 | delivered | 3 |
| BG1219 | 1 | 1 | delivered | 1 |
| BG1311 | 3 | 3 | delivered | 2 |
| BG1323 | 3 | 3 | delivered | 2 |
| BG1361 | 1 | 1 | delivered | 1 |
| BG1398 | 1 | 1 | delivered | 1 |
| BG1404 | 1 | 1 | delivered | 1 |
| BG1429 | 2 | 2 | delivered | 1 |
| BG1450 | 1 | 1 | delivered | 1 |
| BG1473 | 2 | 2 | delivered | 2 |
| BG1513 | 3 | 3 | delivered | 2 |
| BG1562 | 2 | 2 | delivered | 2 |
| BG1564 | 2 | 2 | delivered | 1 |
| BG1583 | 2 | 2 | delivered | 1 |
| BG1591 | 1 | 1 | delivered | 2 |
| BG1598 | 2 | 2 | delivered | 2 |
| BG1606 | 2 | 2 | delivered | 2 |
| BG1608 | 1 | 1 | delivered | 1 |
| BG1650 | 3 | 3 | delivered | 2 |
| BG1658 | 1 | 1 | delivered | 1 |
| BG1673 | 1 | 1 | delivered | 1 |
| BG1692 | 2 | 2 | delivered | 2 |
| BG1698 | 2 | 2 | delivered | 1 |
| BG1736 | 1 | 1 | delivered | 2 |

## Known issues handed over

4 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1738 | Low | A Claude-only run whose sessions all hold their subagents drops a claude -p lane run's delegated total - not-stop-ship, ruled by orchestrator |
| BG1739 | Low | critic.py record refuses a finding whose bare URL is followed by an escaped semicolon - not-stop-ship, ruled by orchestrator |
| BG1740 | Low | reference-review.md lists the optional claim surfaces without the declared pages - not-stop-ship, ruled by orchestrator |
| BG1741 | Low | The retro judges a run whole from another harness's session when the closing session has no closing stamp, and drops a supplied delegated total - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-24T16:52:38Z | c554d224c96c99c8 |

Signing records the principal, the date and this report's fingerprint against RUN-01M866KQ.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | partial over 2 clause(s), 3 seat(s), no seat matched the author; partial: The eighteen Lows the operator kept are fixed with fourteen more from their files; partial: each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 92 leavable |
| batch | caller-check | 32 unit(s) of 32 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 12,716,525 |

Total 12,716,525, of which delegated 7,820,826. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (32 units); reviewer inherit (32 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $153.52 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $8.31 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 1074 subagent transcript(s); total agents 17, calls 2,181, priced 61,893,973. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 305 | 9,836,584 | 15.9% | 83.0% | 8.8% | 8.2% | 266,527 | 269,067 |
| builder | 4 | 789 | 21,245,637 | 34.3% | 62.6% | 21.9% | 15.4% | 15,454 | 173,326 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 5 | 499 | 14,288,379 | 23.1% | 57.6% | 25.9% | 16.5% | 40,106 | 170,870 |
| other | 7 | 588 | 16,523,373 | 26.7% | 54.6% | 28.2% | 17.1% | 40,499 | 159,876 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 1 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45406447622 - 1 push-triggered run(s) on main in the run window |
| Lead time for changes | 8h 14m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 19 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45406447622 - 1 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45406447622 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 1 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is the closing clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

15 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | graduating (CR0751) | 0 | 2 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-011 | widen-after-brief | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 6 | 86 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
| LC-022 | hand-in outside the lane folder | active | 0 | 0 |
| LC-023 | census missed by a narrow commit | active | 0 | 0 |
| LC-024 | second seat past the joint cap | active | 0 | 0 |
| LC-025 | mutant test outside Affects | active | 0 | 0 |
| LC-026 | a builder samples the modules it edits | active | 0 | 0 |
| LC-027 | a self-check recorded out of band | active | 0 | 0 |
| LC-028 | a criterion's premise is probed before it is written | active | 0 | 0 |
| LC-029 | a docs-only repair still mutates its unit's declared tests | active | 0 | 0 |
