# Sprint Report: RUN-01M80RTZ

## Goal

The review, retro, lessons, drive, report and verify scripts lose 28 Medium bugs; each fix's test fails without it

**Verdict: Judged partial** - 25 of the 28 planned Medium bugs are Fixed, each with a test that fails without its fix (every unit approved by an independent qa review, 13 of them in a ruled third round); BG1475, BG1532 and BG1625 were rejected in their ruled third rounds and carry to the next run under BG1707, BG1714 and BG1717. Three Lows filed this run (BG1700 to BG1702) were added and Fixed.

> **Run:** 2026-11-22T04:29:45Z to 2026-11-23T01:28:51Z (21.0h)
> **Verified on:** 7183814f1c916c5cff0d5ddc1b2658ffa8da27ff   **Fingerprint:** 60ac2d7a65abc6b1

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 66 | 66 | 1.0x | 28 of 28 delivered unit(s) |
| Minutes | 385.7 | 1334.9 | 3.46x | measured active minutes (spans or agent minutes) against their forecast, over the 28 of 28 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 745.0 | 1259.1 | 1.69x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0036, RPT0037, RPT0038, RPT0039, RPT0040), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 63,648,288 | 117,125,516 | 1.84x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 20,109,763 (input 9,722 x1, output 4,090,072 x5, cache write 5m 15,198,868 x1.25, cache write 1h 811,101 x2, cache read 760,446,469 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0150, RETRO0151, RETRO0152, RETRO0153, RETRO0154) |
| Tokens | 12,292,632 | 20,109,763 | 1.64x | the whole run: forecast over 28 of 28 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 72 delegated total(s) supplied are not added |
| Priced per point | 964,368 | 1,774,629 | 1.84x | the Priced cost row over the 66 point(s) of the 28 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0150, RETRO0151, RETRO0152, RETRO0153, RETRO0154) |
| Dollar cost | $254.59 | $316.41 | 1.24x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.86 | $4.79 | 1.24x | the Dollar cost row over the 66 point(s) of the 28 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0970 | $4.77 estimated | 11.7 | 35.6 agent minutes, split by points | 372,504 | 346,847 agent tokens, split by points | 1,774,385 priced, split by points |
| BG0982 | $7.16 estimated | 17.5 | 53.4 agent minutes, split by points | 558,756 | 520,271 agent tokens, split by points | 2,661,579 priced, split by points |
| BG0999 | $5.80 estimated | 11.7 | 48.5 agent minutes, split by points | 372,504 | 404,647 agent tokens, split by points | 2,153,688 priced, split by points |
| BG1012 | $6.05 estimated | 11.7 | 62.2 agent minutes, split by points | 372,504 | 386,514 agent tokens, split by points | 2,238,160 priced, split by points |
| BG1050 | $1.80 estimated | 11.7 | 16.5 agent minutes, split by points | 372,504 | 90,874 agent tokens, split by points | 702,948 priced, split by points |
| BG1059 | $6.23 estimated | 17.5 | 46.1 agent minutes, split by points | 558,756 | 309,477 agent tokens, split by points | 2,469,583 priced, split by points |
| BG1060 | $4.15 estimated | 11.7 | 30.7 agent minutes, split by points | 372,504 | 206,319 agent tokens, split by points | 1,646,390 priced, split by points |
| BG1108 | $8.70 estimated | 17.5 | 72.7 agent minutes, split by points | 558,756 | 606,970 agent tokens, split by points | 3,230,532 priced, split by points |
| BG1120 | $5.80 estimated | 11.7 | 48.5 agent minutes, split by points | 372,504 | 404,647 agent tokens, split by points | 2,153,688 priced, split by points |
| BG1124 | $4.77 estimated | 11.7 | 35.6 agent minutes, split by points | 372,504 | 346,847 agent tokens, split by points | 1,774,385 priced, split by points |
| BG1125 | $6.25 estimated | 17.5 | 52.7 agent minutes, split by points | 558,756 | 485,805 agent tokens, split by points | 2,300,669 priced, split by points |
| BG1229 | $8.15 estimated | 17.5 | 82.1 agent minutes, 2 of 3 agent totals split by points | 558,756 | 666,845 agent tokens, 2 of 3 agent totals split by points | 2,915,365 priced, 2 of 3 agent totals split by points |
| BG1265 | $4.17 estimated | 11.7 | 35.1 agent minutes, split by points | 372,504 | 323,870 agent tokens, split by points | 1,533,780 priced, split by points |
| BG1332 | $4.15 estimated | 11.7 | 30.7 agent minutes, split by points | 372,504 | 206,318 agent tokens, split by points | 1,646,390 priced, split by points |
| BG1436 | $4.15 estimated | 11.7 | 30.7 agent minutes, split by points | 372,504 | 206,318 agent tokens, split by points | 1,646,390 priced, split by points |
| BG1463 | $5.06 estimated | 11.7 | 44.5 agent minutes, split by points | 372,504 | 262,466 agent tokens, split by points | 1,972,341 priced, split by points |
| BG1465 | $4.15 estimated | 11.7 | 30.7 agent minutes, split by points | 372,504 | 206,318 agent tokens, split by points | 1,646,390 priced, split by points |
| BG1482 | $5.06 estimated | 11.7 | 44.5 agent minutes, split by points | 372,504 | 262,465 agent tokens, split by points | 1,972,339 priced, split by points |
| BG1483 | $5.06 estimated | 11.7 | 44.5 agent minutes, split by points | 372,504 | 262,465 agent tokens, split by points | 1,972,339 priced, split by points |
| BG1492 | $5.41 estimated | 11.7 | 49.7 agent minutes, split by points | 372,504 | 387,495 agent tokens, split by points | 2,001,644 priced, split by points |
| BG1534 | $12.21 estimated | 17.5 | 112.3 agent minutes, 2 of 3 agent totals split by points | 558,756 | 750,004 agent tokens, 2 of 3 agent totals split by points | 4,403,942 priced, 2 of 3 agent totals split by points |
| BG1578 | $6.61 estimated | 11.7 | 56.5 agent minutes, split by points | 372,504 | 397,063 agent tokens, split by points | 2,427,903 priced, split by points |
| BG1623 | $12.01 estimated | 29.2 | 85.7 agent minutes, split by points | 931,260 | 1,017,716 agent tokens, split by points | 4,256,901 priced, split by points |
| BG1626 | $4.80 estimated | 11.7 | 34.3 agent minutes, split by points | 372,504 | 407,087 agent tokens, split by points | 1,702,760 priced, split by points |
| BG1628 | $2.84 estimated | 11.7 | 28.0 agent minutes, split by points | 372,504 | 230,009 agent tokens, split by points | 1,034,886 priced, split by points |
| BG1700 | $6.25 estimated | 17.5 | 52.7 agent minutes, split by points | 558,756 | 485,804 agent tokens, split by points | 2,300,669 priced, split by points |
| BG1701 | $4.17 estimated | 11.7 | 35.1 agent minutes, split by points | 372,504 | 323,869 agent tokens, split by points | 1,533,780 priced, split by points |
| BG1702 | $4.17 estimated | 11.7 | 35.1 agent minutes, split by points | 372,504 | 323,869 agent tokens, split by points | 1,533,779 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 28 | 72 |
| Delivered of the plan | 25 | 59 |
| Added mid-run and delivered | 3 of 3 added | 7 |
| Dropped | 3 | 13 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 66.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0970 | 2 | 2 | delivered | 2 |
| BG0982 | 3 | 3 | delivered | 2 |
| BG0999 | 2 | 2 | delivered | 3 |
| BG1012 | 2 | 2 | delivered | 2 |
| BG1050 | 2 | 2 | delivered | 1 |
| BG1059 | 3 | 3 | delivered | 2 |
| BG1060 | 2 | 2 | delivered | 2 |
| BG1108 | 3 | 3 | delivered | 3 |
| BG1120 | 2 | 2 | delivered | 3 |
| BG1124 | 2 | 2 | delivered | 2 |
| BG1125 | 3 | 3 | delivered | 2 |
| BG1229 | 3 | 3 | delivered | 3 |
| BG1265 | 2 | 2 | delivered | 2 |
| BG1332 | 2 | 2 | delivered | 2 |
| BG1436 | 2 | 2 | delivered | 2 |
| BG1463 | 2 | 2 | delivered | 3 |
| BG1465 | 2 | 2 | delivered | 2 |
| BG1475 | 3 | 3 | dropped - carried at the review cap: BG1707 | 3 |
| BG1482 | 2 | 2 | delivered | 3 |
| BG1483 | 2 | 2 | delivered | 3 |
| BG1492 | 2 | 2 | delivered | 3 |
| BG1532 | 5 | 5 | dropped - carried at the review cap: BG1714 | 3 |
| BG1534 | 3 | 3 | delivered | 3 |
| BG1578 | 2 | 2 | delivered | 2 |
| BG1623 | 5 | 5 | delivered | 2 |
| BG1625 | 5 | 5 | dropped - carried at the review cap: BG1717 | 3 |
| BG1626 | 2 | 2 | delivered | 2 |
| BG1628 | 2 | 2 | delivered | 1 |
| BG1700 | 3 | 3 | added - Low found in run twenty-two in critic.py; built in lane C2 with critic.py's Mediums (BG1700 slows show past the real-tree test's 120 s bound under load); delivered | 2 |
| BG1701 | 2 | 2 | added - Low found in run twenty-two in critic.py; built in lane C2 with critic.py's Mediums (BG1700 slows show past the real-tree test's 120 s bound under load); delivered | 2 |
| BG1702 | 2 | 2 | added - Low found in run twenty-two in critic.py; built in lane C2 with critic.py's Mediums (BG1700 slows show past the real-tree test's 120 s bound under load); delivered | 2 |

## Known issues handed over

8 open finding(s) raised in the run, 2 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1707 | Medium | BG1475 did not converge in review: round 2 REJECT findings |
| BG1714 | Medium | BG1532 did not converge in review: round 2 REJECT findings |
| BG1717 | Medium | BG1625 did not converge in review: round 2 REJECT findings |
| CR0750 | Medium | Prevent or retire lesson LC-004 (premise not executed) |
| BG1699 | Low | lane land's commit bound is a fixed 1800 seconds that no setting or flag changes, so a lane whose commit selects most of the suite is stopped whenever the host is loaded |
| BG1708 | Low | verify_ac.py ts-check reports two test ids pytest collects: a file under a dotted directory in importlib form, and a def whose decorator gives it a docstring with an example |
| BG1712 | Low | Nine whole-file rewrites of tracked workspace files still truncate in place instead of going through sdlc_md.atomic_write, so an interrupted write can leave the file half-written |
| BG1713 | Low | Two lanes of one parallel drive wave create their worktrees at the same moment, and git's concurrent worktree add can refuse one, stopping that unit at build |
| cost | close gap | RETRO0155: 1,774,629 priced input-equivalent tokens per gate-cleared point (117,125,516 over 66 point(s)) is 1.84 x the baseline 964,368 per point, the median of the 5 most recent priced runs (RETRO0150, RETRO0151, RETRO0152, RETRO0153, RETRO0154), over 1.5 x. Per unit (priced span): BG0970 61,456,467; BG0982 61,987,305; BG1012 59,417,560; BG1050 28,131,437; BG1059 81,069,112; BG1060 81,132,710; BG1124 65,884,429; BG1125 51,474,154; BG1265 51,492,312; BG1332 81,319,672; BG1436 81,439,705; BG1465 81,728,880; BG1578 52,507,288; BG1623 72,357,955; BG1626 72,484,236; BG1628 39,338,283; BG1700 50,797,851; BG1701 50,988,895; BG1702 51,071,907; BG1534 NOT MEASURED; BG0999 NOT MEASURED; BG1108 NOT MEASURED; BG1120 NOT MEASURED; BG1463 NOT MEASURED; BG1482 NOT MEASURED; BG1483 NOT MEASURED; BG1229 NOT MEASURED; BG1492 NOT MEASURED; unattributed remainder 0, clamped from -1,058,954,642: the unit spans overlap, so their costs sum past the run's total. The retro names the cause under `## Cost` |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 8 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-23T01:36:31Z | 60ac2d7a65abc6b1 |

Signing records the principal, the date and this report's fingerprint against RUN-01M80RTZ.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | achieved over 2 clause(s), 3 seat(s), no seat matched the author; achieved (1 seat(s) silent): The review, retro, lessons, drive, report and verify scripts lose 28 Medium bugs; achieved (2 seat(s) silent): each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 294 leavable |
| batch | caller-check | 28 unit(s) of 28 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 20,109,763 |

Total 20,109,763, of which delegated 13,953,721. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (28 units); reviewer inherit (28 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $316.41 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 958 subagent transcript(s); total agents 48, calls 4,676, priced 117,125,516. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 596 | 18,317,264 | 15.6% | 83.0% | 8.9% | 8.2% | 191,811 | 256,404 |
| builder | 6 | 1,278 | 40,022,223 | 34.2% | 63.2% | 21.7% | 15.1% | 14,987 | 203,273 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 13 | 1,525 | 36,022,979 | 30.8% | 67.4% | 15.9% | 16.6% | 15,265 | 162,318 |
| other | 28 | 1,277 | 22,763,050 | 19.4% | 49.5% | 20.1% | 30.4% | 19,932 | 91,097 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 3 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45092584968/45068223727/45018423519 - 3 push-triggered run(s) on main in the run window |
| Lead time for changes | 20h 15m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 38 commit(s) |
| Change failure rate | 33% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45092584968/45068223727/45018423519 - 3 deployment(s); 1 failed on 30eb84a51fa4d6ed8e283d7b2a84d561ba9cb9e4 |
| Time to restore | not restored | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45068223727 - main went red at run 45068223727, and no push-triggered run created after it concluded success in the run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 13 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

0 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

8 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 1 | 1 |
| LC-004 | premise not executed | graduating (CR0750) | 1 | 3 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-011 | widen-after-brief | active | 1 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 9 | 70 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
