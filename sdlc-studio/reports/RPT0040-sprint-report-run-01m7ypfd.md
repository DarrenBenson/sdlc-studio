# Sprint Report: RUN-01M7YPFD

## Goal

The sprint, lane, transition and verify scripts lose 32 Medium bugs; each fix's test fails without it

**Verdict: Judged partial** - 31 of the 32 Medium bugs in the sprint, lane, transition and verify scripts are Fixed, each with a test its mutation pass shows fails without the fix; BG1534 is carried open after its ruled third round rejected

> **Run:** 2026-11-21T09:28:54Z to 2026-11-22T03:48:19Z (18.3h)
> **Verified on:** 681d7fb89dcaeb5928ee46028df007796fe91da9   **Fingerprint:** 125fd680af35edeb

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 77 | 79 | 1.03x | 31 of 31 delivered unit(s) |
| Minutes | 292.1 | 4444.6 | 15.22x | measured active minutes (spans or agent minutes) against their forecast, over the 19 of 31 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 869.1 | 1099.4 | 1.26x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0035, RPT0036, RPT0037, RPT0038, RPT0039), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 61,589,143 | 107,826,355 | 1.75x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 16,928,343 (input 9,348 x1, output 3,923,725 x5, cache write 5m 12,313,377 x1.25, cache write 1h 681,893 x2, cache read 714,428,746 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0149, RETRO0150, RETRO0151, RETRO0152, RETRO0153) |
| Tokens | 14,341,404 | 16,928,343 | 1.18x | the whole run: forecast over 31 of 31 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 74 delegated total(s) supplied are not added |
| Priced per point | 799,859 | 1,364,891 | 1.71x | the Priced cost row over the 79 point(s) of the 31 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0149, RETRO0150, RETRO0151, RETRO0152, RETRO0153) |
| Dollar cost | $246.36 | $288.42 | 1.17x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.20 | $3.65 | 1.14x | the Dollar cost row over the 79 point(s) of the 31 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0954 | $12.25 estimated | 17.5 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 558,756 | 731,493 agent tokens, split by points | 4,620,078 priced, split by points |
| BG0956 | $12.25 estimated | 17.5 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 558,756 | 731,492 agent tokens, split by points | 4,620,076 priced, split by points |
| BG0961 | $7.03 estimated | 17.5 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 558,756 | 564,919 agent tokens, split by points | 2,409,717 priced, split by points |
| BG0983 | $6.80 estimated | 17.5 | 572.1 | 558,756 | 522,696 agent tokens, split by points | 2,532,917 priced, split by points |
| BG0985 | $1.76 estimated | 5.8 | 477.2 | 186,252 | 79,560 agent tokens, split by points | 690,518 priced, split by points |
| BG0987 | $11.33 estimated | 17.5 | 574.0 | 558,756 | 871,159 agent tokens, split by points | 4,221,528 priced, split by points |
| BG1021 | $2.40 estimated | 11.7 | 171.4 | 372,504 | 105,308 agent tokens, split by points | 953,970 priced, split by points |
| BG1023 | $4.69 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 376,612 agent tokens, split by points | 1,606,477 priced, split by points |
| BG1051 | $2.40 estimated | 11.7 | 173.2 | 372,504 | 105,308 agent tokens, split by points | 953,970 priced, split by points |
| BG1058 | $2.40 estimated | 11.7 | 180.5 | 372,504 | 105,308 agent tokens, split by points | 953,970 priced, split by points |
| BG1107 | $4.41 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 206,286 agent tokens, split by points | 1,721,356 priced, split by points |
| BG1399 | $6.60 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 303,230 agent tokens, split by points | 2,588,269 priced, split by points |
| BG1400 | $3.68 estimated | 11.7 | 19.3 agent minutes (1 of 2 agents), split by points | 372,504 | 230,198 agent tokens, split by points | 1,391,963 priced, split by points |
| BG1406 | $1.55 estimated | 11.7 | 6.3 agent minutes (1 of 2 agents), split by points | 372,504 | 83,124 agent tokens, split by points | 601,181 priced, split by points |
| BG1409 | $6.60 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 303,230 agent tokens, split by points | 2,588,269 priced, split by points |
| BG1413 | $2.85 estimated | 11.7 | 241.4 | 372,504 | 143,378 agent tokens, split by points | 1,103,212 priced, split by points |
| BG1448 | $3.87 estimated | 29.2 | 15.7 agent minutes (1 of 2 agents), split by points | 931,260 | 207,808 agent tokens, split by points | 1,502,954 priced, split by points |
| BG1470 | $7.37 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 579,763 agent tokens, 1 of 3 agent totals split by points | 2,502,557 priced, 1 of 3 agent totals split by points |
| BG1477 | $5.89 estimated | 11.7 | 50.9 agent minutes (2 of 3 agents), 2 of 3 agent totals split by points | 372,504 | 375,022 agent tokens, 2 of 3 agent totals split by points | 2,144,294 priced, 2 of 3 agent totals split by points |
| BG1491 | $3.68 estimated | 11.7 | 19.3 agent minutes (1 of 2 agents), split by points | 372,504 | 230,196 agent tokens, split by points | 1,391,961 priced, split by points |
| BG1512 | $3.87 estimated | 29.2 | 15.7 agent minutes (1 of 2 agents), split by points | 931,260 | 207,807 agent tokens, split by points | 1,502,954 priced, split by points |
| BG1539 | $3.87 estimated | 29.2 | 15.7 agent minutes (1 of 2 agents), split by points | 931,260 | 207,807 agent tokens, split by points | 1,502,954 priced, split by points |
| BG1582 | $5.27 estimated | 17.5 | 478.0 | 558,756 | 238,681 agent tokens, split by points | 2,071,554 priced, split by points |
| BG1590 | $5.27 estimated | 17.5 | 478.6 | 558,756 | 238,681 agent tokens, split by points | 2,071,554 priced, split by points |
| BG1609 | $5.95 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 486,327 agent tokens, 2 of 3 agent totals split by points | 2,146,731 priced, 2 of 3 agent totals split by points |
| BG1610 | $4.80 estimated | 11.7 | 509.4 | 372,504 | 225,002 agent tokens, split by points | 1,879,388 priced, split by points |
| BG1614 | $6.60 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 303,229 agent tokens, split by points | 2,588,268 priced, split by points |
| BG1624 | $6.60 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 303,228 agent tokens, split by points | 2,588,267 priced, split by points |
| BG1627 | $6.60 estimated | 11.7 | NOT MEASURED - 0 of its 3 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 303,227 agent tokens, split by points | 2,588,267 priced, split by points |
| BG1629 | $3.68 estimated | 11.7 | 19.3 agent minutes (1 of 2 agents), split by points | 372,504 | 230,197 agent tokens, split by points | 1,391,962 priced, split by points |
| BG0981 | $4.53 estimated | 11.7 | 426.5 | 372,504 | 348,464 agent tokens, split by points | 1,688,610 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 32 | 81 |
| Delivered of the plan | 30 | 75 |
| Added mid-run and delivered | 1 of 1 added | 2 |
| Dropped | 2 | 6 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 79.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0954 | 3 | 3 | delivered | 3 |
| BG0956 | 3 | 3 | delivered | 3 |
| BG0961 | 3 | 3 | delivered | 3 |
| BG0983 | 3 | 3 | delivered | 2 |
| BG0985 | 1 | 1 | delivered | 2 |
| BG0987 | 3 | 5 | delivered | 2 |
| BG1021 | 2 | 2 | delivered | 1 |
| BG1023 | 2 | 2 | delivered | 3 |
| BG1051 | 2 | 2 | delivered | 1 |
| BG1058 | 2 | 2 | delivered | 1 |
| BG1107 | 2 | 2 | delivered | 3 |
| BG1399 | 2 | 2 | delivered | 3 |
| BG1400 | 2 | 2 | delivered | 2 |
| BG1406 | 2 | 2 | delivered | 2 |
| BG1409 | 2 | 2 | delivered | 3 |
| BG1413 | 2 | 2 | delivered | 1 |
| BG1448 | 5 | 5 | delivered | 2 |
| BG1470 | 2 | 2 | delivered | 3 |
| BG1477 | 2 | 2 | delivered | 3 |
| BG1491 | 2 | 2 | delivered | 2 |
| BG1512 | 5 | 5 | delivered | 2 |
| BG1534 | 3 | 3 | dropped - carried at the review cap: BG1682 | 3 |
| BG1539 | 5 | 5 | delivered | 2 |
| BG1569 | 3 | 5 | dropped - swap: BG1569's Delivered status needs a corpus migration of 56 RFCs, a ruling on 20 RFCs with no change requests, and readiness.py and handoff.py: re-sized 5 to 8 for its own lane in run twenty-two. BG0981 (2 points, groomed, sprint.py and verify_ac.py) joins lane S2 so the goal's 32 holds. | 0 |
| BG1582 | 3 | 3 | delivered | 2 |
| BG1590 | 3 | 3 | delivered | 2 |
| BG1609 | 2 | 2 | delivered | 3 |
| BG1610 | 2 | 2 | delivered | 2 |
| BG1614 | 2 | 2 | delivered | 3 |
| BG1624 | 2 | 2 | delivered | 3 |
| BG1627 | 2 | 2 | delivered | 3 |
| BG1629 | 2 | 2 | delivered | 2 |
| BG0981 | 2 | 2 | added - no reason recorded; delivered | 2 |

## Known issues handed over

10 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1678 | Medium | This repo's RFCs need migrating to BG1569's Delivered status, and the 20 with no change requests need a status ruling - deferred, ruled by orchestrator |
| BG1682 | Medium | BG1534 did not converge in review: round 2 REJECT findings - deferred, ruled by orchestrator |
| BG1676 | Low | reconcile stops on an index that is not UTF-8 without naming the file or how to fix it - not-stop-ship, ruled by orchestrator |
| BG1677 | Low | lane land's sibling-script timeout stops only the script, leaving its child processes running - not-stop-ship, ruled by orchestrator |
| BG1679 | Low | transition.py moves a story from Draft to Ready without checking its Definition of Ready, so Draft to Ready to Done skips the gate BG0954 adds - not-stop-ship, ruled by orchestrator |
| BG1692 | Low | The close's goal judgement never rules a defect on the clause basis: _open_defects never reads Falsifies - not-stop-ship, ruled by orchestrator |
| BG1694 | Low | test_kill_grace_interrupt reads the deaf child's pid file before the child has written it, so it fails under load - not-stop-ship, ruled by orchestrator |
| BG1695 | Low | lane land names a conflicting path that holds a space as two paths - not-stop-ship, ruled by orchestrator |
| BG1696 | Low | sprint drive's headless review passes no effort, while the sprint report says the reviewer ran at the plan's stamp - not-stop-ship, ruled by orchestrator |
| BG1698 | Low | A unit approved in a ruled round past the cap stays dropped from the batch, so the close and the report do not credit it - not-stop-ship, ruled by orchestrator |
| cost | close gap | RETRO0154: 1,364,891 priced input-equivalent tokens per gate-cleared point (107,826,355 over 79 point(s)) is 1.71 x the baseline 799,859 per point, the median of the 5 most recent priced runs (RETRO0149, RETRO0150, RETRO0151, RETRO0152, RETRO0153), over 1.5 x. Per unit (priced span): BG0983 81,757,212; BG0985 70,914,462; BG0987 81,814,720; BG1021 29,881,394; BG1051 30,136,217; BG1058 31,414,144; BG1400 69,170,973; BG1406 67,767,986; BG1413 44,820,462; BG1448 67,767,986; BG1491 69,170,973; BG1512 67,767,986; BG1539 67,767,986; BG1582 71,037,848; BG1590 71,037,848; BG1610 75,131,048; BG1629 104,051,439; BG0981 57,172,993; BG0961 NOT MEASURED; BG1023 NOT MEASURED; BG0954 NOT MEASURED; BG0956 NOT MEASURED; BG1107 NOT MEASURED; BG1399 NOT MEASURED; BG1409 NOT MEASURED; BG1614 NOT MEASURED; BG1624 NOT MEASURED; BG1627 NOT MEASURED; BG1609 NOT MEASURED; BG1470 NOT MEASURED; BG1477 NOT MEASURED; unattributed remainder 0, clamped from -1,050,757,322: the unit spans overlap, so their costs sum past the run's total. The retro names the cause under `## Cost` |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M7YPFD.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | partial over 2 clause(s), 3 seat(s), no seat matched the author; achieved: The sprint, lane, transition and verify scripts lose 32 Medium bugs; UNANSWERED (3 seat(s) silent): each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 312 leavable |
| batch | caller-check | 31 unit(s) of 31 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 16,928,343 |

Total 16,928,343, of which delegated 10,513,657. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (32 units); reviewer inherit (32 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $288.42 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 908 subagent transcript(s); total agents 47, calls 4,536, priced 107,826,355. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 436 | 13,740,795 | 12.7% | 81.6% | 9.9% | 8.4% | 328,927 | 258,870 |
| builder | 6 | 1,266 | 34,494,182 | 32.0% | 69.4% | 16.0% | 14.6% | 14,962 | 192,503 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 14 | 1,346 | 31,035,280 | 28.8% | 65.0% | 15.6% | 19.4% | 15,206 | 152,797 |
| other | 26 | 1,488 | 28,556,098 | 26.5% | 56.4% | 17.6% | 26.0% | 14,816 | 111,016 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 3 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44971031189/44950498303/44908738920 - 3 push-triggered run(s) on main in the run window |
| Lead time for changes | 15h 30m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 33 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44971031189/44950498303/44908738920 - 3 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44971031189/44950498303/44908738920 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 14 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

0 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 5 | 61 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
