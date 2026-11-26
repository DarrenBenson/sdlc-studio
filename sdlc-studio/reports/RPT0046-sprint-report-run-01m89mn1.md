# Sprint Report: RUN-01M89MN1

## Goal

v6.5.0 is ready to tag: its notes, pages and specs say only what the code does, under the release bar

**Verdict: Judged partial** - The notes, pages and specs of 6.5 as first scoped say only what the code does (US1327-US1329, US1331 Done) and the release bar holds (48 open, all Low), but v6.5.0 is not yet ready to tag: the operator widened the release (D0635, D0638), so the cut (US1330) and the widened paperwork (US1341-US1343) moved to run twenty-eight.

> **Run:** 2026-11-25T15:15:20Z to 2026-11-26T03:41:59Z (12.4h)
> **Verified on:** 213151b4520fde2619f8339e0598b2c09ffb0791   **Fingerprint:** 8df94368173562b0

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 22 | 22 | 1.0x | 6 of 6 delivered unit(s) |
| Minutes | 128.4 | 1622.3 | 12.63x | measured active minutes (spans or agent minutes) against their forecast, over the 6 of 6 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 245.9 | 746.6 | 3.04x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0041, RPT0042, RPT0043, RPT0044, RPT0045), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 33,545,424 | 76,801,452 | 2.29x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 17,294,968 (input 5,302 x1, output 2,325,289 x5, cache write 5m 13,942,166 x1.25, cache write 1h 1,022,211 x2, cache read 456,975,753 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0155, RETRO0156, RETRO0157, RETRO0158, RETRO0159) |
| Tokens | 4,097,544 | 17,294,968 | 4.22x | the whole run: forecast over 6 of 6 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 6 delegated total(s) supplied are not added |
| Priced per point | 1,524,792 | 3,490,975 | 2.29x | the Priced cost row over the 22 point(s) of the 6 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0155, RETRO0156, RETRO0157, RETRO0158, RETRO0159) |
| Dollar cost | $134.18 | $215.81 | 1.61x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $6.10 | $9.81 | 1.61x | the Dollar cost row over the 22 point(s) of the 6 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| US1327 | $21.01 estimated | 29.2 | 365.1 agent minutes | 931,260 | 2,336,805 agent tokens | 6,856,454 priced |
| US1328 | $18.52 estimated | 29.2 | 317.8 agent minutes | 931,260 | 2,375,283 agent tokens | 5,816,239 priced |
| US1329 | $14.23 estimated | 29.2 | 311.7 agent minutes | 931,260 | 1,051,139 agent tokens | 5,227,615 priced |
| US1331 | $28.78 estimated | 17.5 | 350.5 agent minutes | 558,756 | 3,175,669 agent tokens | 9,473,696 priced |
| BG1762 | $2.90 estimated | 5.8 | 85.4 agent minutes | 186,252 | 312,565 agent tokens | 884,116 priced |
| BG1763 | $11.31 estimated | 17.5 | 191.8 agent minutes | 558,756 | 1,242,207 agent tokens | 3,666,608 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 4 | 23 |
| Delivered of the plan | 3 | 15 |
| Added mid-run and delivered | 3 of 3 added | 7 |
| Dropped | 1 | 8 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 22.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1327 | 5 | 5 | delivered | 3 |
| US1328 | 5 | 5 | delivered | 2 |
| US1329 | 5 | 5 | delivered | 2 |
| US1330 | 8 | 5 | dropped - D0635: v6.5.0's scope grows, so the cut must follow the new units and the paperwork describing them; US1330 becomes the last unit of run twenty-eight | 0 |
| US1331 | 3 | 3 | added - discharged carried at the review cap: BG1761; delivered | 5 |
| BG1762 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1763 | 3 | 3 | added - discharged carried at the review cap: BG1766; delivered | 4 |

## Known issues handed over

6 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0752 | Medium | The run breaker reads spend as well as minutes and units: it warns at 75 and 95 per cent, lets the unit in flight finish, and a raise is a recorded decision - not-stop-ship, ruled by orchestrator |
| CR0753 | Medium | The run report compares each role's cache-read share with the project's earlier runs, and the retro names a fall - not-stop-ship, ruled by orchestrator |
| CR0755 | Medium | Say the person owns the PRD and the PVD, and the seat holds delegated authority to check the work meets them - not-stop-ship, ruled by orchestrator |
| BG1764 | Low | The cost anatomy reads no reviewer recorded with its seat, so the report's reviewer row shows 0 agents and review spend lands under other - not-stop-ship, ruled by orchestrator |
| BG1765 | Low | A carry is always filed at Medium, so a unit that checks a release bar barring Medium cannot close its own carry - not-stop-ship, ruled by orchestrator |
| CR0754 | Low | routing.effort takes an effort per kind of unit, as routing.floor takes a tier, set from the bench's effort arm - not-stop-ship, ruled by orchestrator |
| cost | close gap | RETRO0160: 3,490,975 priced input-equivalent tokens per gate-cleared point (76,801,452 over 22 point(s)) is 2.29 x the baseline 1,524,792 per point, the median of the 5 most recent priced runs (RETRO0155, RETRO0156, RETRO0157, RETRO0158, RETRO0159), over 1.5 x. Per unit (priced span): US1328 33,046,844; US1329 33,236,321; US1327 38,908,960; US1331 34,107,769; BG1762 11,616,173; BG1763 28,140,204; unattributed remainder 0, clamped from -102,254,819: the unit spans overlap, so their costs sum past the run's total. The retro names the cause under `## Cost` |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M89MN1.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | UNANSWERED over 1 clause(s), 3 seat(s), no seat matched the author; UNANSWERED (3 seat(s) silent): v6.5.0 is ready to tag: its notes, pages and specs say only what the code does, under the release bar |
| open defects | defects vs goal | 0 BLOCKING, 48 leavable |
| batch | caller-check | 6 unit(s) of 6 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 17,294,968 |

Total 17,294,968, of which delegated 10,493,668. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (4 units); reviewer inherit (4 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $215.81 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 1129 subagent transcript(s); total agents 20, calls 2,491, priced 76,801,452. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 586 | 19,620,215 | 25.5% | 79.7% | 10.4% | 9.9% | 339,081 | 268,559 |
| builder | 6 | 917 | 31,924,728 | 41.6% | 48.5% | 37.6% | 13.9% | 15,566 | 179,242 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| other | 13 | 988 | 25,256,509 | 32.9% | 57.8% | 21.5% | 20.8% | 25,569 | 152,029 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45738318335/45706116760/45687520241/45668825034 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 12h 11m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 28 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45738318335/45706116760/45687520241/45668825034 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45738318335/45706116760/45687520241/45668825034 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 7 time(s), 0 of them by citing a
precedent; the operator ruled 4 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is the closing clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | 1 candidate catch(es) over 3 runs |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| neutrality | 2 | 1 | 1 | 1 candidate catch(es) over 3 runs |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

20 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | graduating (CR0751) | 1 | 3 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 101 |
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
| LC-030 | a high-risk carry round briefs both seats at once | active | 0 | 0 |
| LC-031 | the paperwork commit stages every file a recorded row cites | active | 0 | 0 |
| LC-032 | a builder adding a timing test runs the census before hand-in | active | 0 | 0 |
| LC-033 | a bug groomed for a lane names its fragment | active | 0 | 0 |
| LC-034 | the page moves with the corpus | active | 0 | 0 |
| LC-035 | two seats' parallel REJECTs | active | 0 | 0 |
