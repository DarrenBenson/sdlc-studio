# Sprint Report: RUN-01M87B5M

## Goal

Open bugs fall under fifty as forty-six Lows are fixed; each fix's test fails without it

**Verdict: Judged achieved** - Open bugs fell from 92 to 46, all Low and none at Medium or above. All 51 batch units are Fixed on an independent approval: the 46 planned Lows, BG1752 and the four groomed Lows added when the run's own filings held the count at 50. Each unit landed with its author's mutation report answered in full, and each reviewer ran its own mutation pass against the unit's tests.

> **Run:** 2026-11-24T17:55:20Z to 2026-11-25T13:32:50Z (19.6h)
> **Verified on:** e66fb1cb276e9a5dfd21d6df27dccfee130f465b   **Fingerprint:** c13eb02cbd5f25dc

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 77 | 77 | 1.0x | 51 of 51 delivered unit(s) |
| Minutes | 448.7 | 4878.8 | 10.87x | measured active minutes (spans or agent minutes) against their forecast, over the 51 of 51 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 862.0 | 1177.5 | 1.37x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0040, RPT0041, RPT0042, RPT0043, RPT0044), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 105,096,607 | 146,414,637 | 1.39x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 33,117,619 (input 9,590 x1, output 3,531,434 x5, cache write 5m 28,428,549 x1.25, cache write 1h 1,148,046 x2, cache read 909,160,988 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0154, RETRO0155, RETRO0156, RETRO0157, RETRO0158) |
| Tokens | 14,341,404 | 33,117,619 | 2.31x | the whole run: forecast over 51 of 51 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 52 delegated total(s) supplied are not added |
| Priced per point | 1,364,891 | 1,901,489 | 1.39x | the Priced cost row over the 77 point(s) of the 51 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0154, RETRO0155, RETRO0156, RETRO0157, RETRO0158) |
| Dollar cost | $420.39 | $362.06 | 0.86x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $5.46 | $4.70 | 0.86x | the Dollar cost row over the 77 point(s) of the 51 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0952 | $0.3189 estimated | 5.8 | 7.9 agent minutes, split by points | 186,252 | 29,544 agent tokens, split by points | 250,331 priced, split by points |
| BG0960 | $18.47 estimated | 11.7 | 231.6 agent minutes, split by points | 372,504 | 1,536,126 agent tokens, split by points | 6,815,868 priced, split by points |
| BG0969 | $2.12 estimated | 5.8 | 18.5 agent minutes, split by points | 186,252 | 188,595 agent tokens, split by points | 766,099 priced, split by points |
| BG0973 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,123 priced, split by points |
| BG1006 | $7.35 estimated | 11.7 | 77.7 agent minutes, split by points | 372,504 | 613,943 agent tokens, split by points | 2,685,286 priced, split by points |
| BG1013 | $2.12 estimated | 5.8 | 18.5 agent minutes, split by points | 186,252 | 188,595 agent tokens, split by points | 766,099 priced, split by points |
| BG1017 | $2.69 estimated | 11.7 | 65.8 agent minutes, split by points | 372,504 | 266,837 agent tokens, split by points | 2,194,245 priced, split by points |
| BG1026 | $4.87 estimated | 5.8 | 378.2 agent minutes | 186,252 | 752,511 agent tokens | 3,569,850 priced |
| BG1068 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,122 priced, split by points |
| BG1103 | $2.12 estimated | 5.8 | 18.5 agent minutes, split by points | 186,252 | 188,595 agent tokens, split by points | 766,099 priced, split by points |
| BG1128 | $7.35 estimated | 11.7 | 77.7 agent minutes, split by points | 372,504 | 613,943 agent tokens, split by points | 2,685,286 priced, split by points |
| BG1151 | $2.47 estimated | 17.5 | 127.9 agent minutes, split by points | 558,756 | 306,449 agent tokens, split by points | 1,878,582 priced, split by points |
| BG1152 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,122 priced, split by points |
| BG1193 | $0.3189 estimated | 5.8 | 7.9 agent minutes, split by points | 186,252 | 29,544 agent tokens, split by points | 250,331 priced, split by points |
| BG1237 | $7.35 estimated | 11.7 | 77.7 agent minutes, split by points | 372,504 | 613,943 agent tokens, split by points | 2,685,286 priced, split by points |
| BG1251 | $18.47 estimated | 11.7 | 231.6 agent minutes, split by points | 372,504 | 1,536,126 agent tokens, split by points | 6,815,868 priced, split by points |
| BG1269 | $18.47 estimated | 11.7 | 231.6 agent minutes, split by points | 372,504 | 1,536,126 agent tokens, split by points | 6,815,867 priced, split by points |
| BG1287 | $3.67 estimated | 5.8 | 38.9 agent minutes, split by points | 186,252 | 306,972 agent tokens, split by points | 1,342,643 priced, split by points |
| BG1292 | $4.25 estimated | 11.7 | 37.1 agent minutes, split by points | 372,504 | 377,191 agent tokens, split by points | 1,532,197 priced, split by points |
| BG1296 | $11.64 estimated | 5.8 | 388.1 agent minutes | 186,252 | 1,546,531 agent tokens | 9,085,746 priced |
| BG1304 | $25.25 estimated | 5.8 | 674.0 agent minutes | 186,252 | 4,270,568 agent tokens | 18,853,249 priced |
| BG1307 | $0.6377 estimated | 11.7 | 15.9 agent minutes, split by points | 372,504 | 59,087 agent tokens, split by points | 500,662 priced, split by points |
| BG1328 | $2.69 estimated | 11.7 | 65.8 agent minutes, split by points | 372,504 | 266,836 agent tokens, split by points | 2,194,245 priced, split by points |
| BG1335 | $9.24 estimated | 5.8 | 115.8 agent minutes, split by points | 186,252 | 768,063 agent tokens, split by points | 3,407,934 priced, split by points |
| BG1342 | $2.93 estimated | 5.8 | 32.5 agent minutes, split by points | 186,252 | 280,124 agent tokens, split by points | 1,022,613 priced, split by points |
| BG1389 | $0.8223 estimated | 5.8 | 42.6 agent minutes, split by points | 186,252 | 102,150 agent tokens, split by points | 626,194 priced, split by points |
| BG1424 | $2.93 estimated | 5.8 | 32.5 agent minutes, split by points | 186,252 | 280,124 agent tokens, split by points | 1,022,613 priced, split by points |
| BG1427 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,123 priced, split by points |
| BG1449 | $7.75 estimated | 5.8 | 96.2 agent minutes, split by points | 186,252 | 736,267 agent tokens, split by points | 2,711,298 priced, split by points |
| BG1454 | $2.93 estimated | 5.8 | 32.5 agent minutes, split by points | 186,252 | 280,124 agent tokens, split by points | 1,022,613 priced, split by points |
| BG1476 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,123 priced, split by points |
| BG1495 | $5.86 estimated | 11.7 | 64.9 agent minutes, split by points | 372,504 | 560,248 agent tokens, split by points | 2,045,226 priced, split by points |
| BG1589 | $1.95 estimated | 5.8 | 15.8 agent minutes, split by points | 186,252 | 182,815 agent tokens, split by points | 684,109 priced, split by points |
| BG1594 | $8.80 estimated | 17.5 | 97.4 agent minutes, split by points | 558,756 | 840,373 agent tokens, split by points | 3,067,839 priced, split by points |
| BG1595 | $2.93 estimated | 5.8 | 32.5 agent minutes, split by points | 186,252 | 280,124 agent tokens, split by points | 1,022,613 priced, split by points |
| BG1616 | $1.71 estimated | 11.7 | 53.2 agent minutes, split by points | 372,504 | 190,669 agent tokens, split by points | 1,373,620 priced, split by points |
| BG1619 | $3.90 estimated | 11.7 | 31.5 agent minutes, split by points | 372,504 | 365,631 agent tokens, split by points | 1,368,218 priced, split by points |
| BG1641 | $1.71 estimated | 11.7 | 53.2 agent minutes, split by points | 372,504 | 190,669 agent tokens, split by points | 1,373,619 priced, split by points |
| BG1649 | $4.84 estimated | 17.5 | 122.0 agent minutes, 1 of 2 agent totals split by points | 558,756 | 428,182 agent tokens, 1 of 2 agent totals split by points | 2,886,712 priced, 1 of 2 agent totals split by points |
| BG1657 | $1.34 estimated | 5.8 | 32.9 agent minutes, split by points | 186,252 | 133,418 agent tokens, split by points | 1,097,123 priced, split by points |
| BG1661 | $38.77 estimated | 29.2 | 481.0 agent minutes, split by points | 931,260 | 3,681,335 agent tokens, split by points | 13,556,487 priced, split by points |
| BG1677 | $0.8558 estimated | 5.8 | 26.6 agent minutes, split by points | 186,252 | 95,334 agent tokens, split by points | 686,810 priced, split by points |
| BG1695 | $0.8558 estimated | 5.8 | 26.6 agent minutes, split by points | 186,252 | 95,334 agent tokens, split by points | 686,810 priced, split by points |
| BG1713 | $1.71 estimated | 11.7 | 53.2 agent minutes, split by points | 372,504 | 190,669 agent tokens, split by points | 1,373,619 priced, split by points |
| BG1719 | $1.12 estimated | 11.7 | 20.6 agent minutes, split by points | 372,504 | 126,805 agent tokens, split by points | 879,735 priced, split by points |
| BG1739 | $0.5615 estimated | 5.8 | 10.3 agent minutes, split by points | 186,252 | 63,402 agent tokens, split by points | 439,868 priced, split by points |
| BG1752 | $2.84 estimated | 5.8 | 42.8 agent minutes | 186,252 | 261,221 agent tokens | 919,977 priced |
| BG1282 | $15.87 estimated | 5.8 | 112.4 agent minutes, split by points | 186,252 | 1,303,264 agent tokens, split by points | 5,659,493 priced, split by points |
| BG1412 | $2.96 estimated | 5.8 | 18.2 agent minutes, split by points | 186,252 | 183,238 agent tokens, split by points | 1,106,376 priced, split by points |
| BG1497 | $35.57 estimated | 5.8 | 257.8 agent minutes | 186,252 | 3,090,793 agent tokens | 12,448,787 priced |
| BG1504 | $2.96 estimated | 5.8 | 18.2 agent minutes, split by points | 186,252 | 183,237 agent tokens, split by points | 1,106,376 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 46 | 72 |
| Delivered of the plan | 46 | 72 |
| Added mid-run and delivered | 5 of 5 added | 5 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 77.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0952 | 1 | 1 | delivered | 1 |
| BG0960 | 2 | 2 | delivered | 4 |
| BG0969 | 1 | 1 | delivered | 2 |
| BG0973 | 1 | 1 | delivered | 2 |
| BG1006 | 2 | 2 | delivered | 3 |
| BG1013 | 1 | 1 | delivered | 2 |
| BG1017 | 2 | 2 | delivered | 2 |
| BG1026 | 1 | 1 | delivered | 3 |
| BG1068 | 1 | 1 | delivered | 2 |
| BG1103 | 1 | 1 | delivered | 2 |
| BG1128 | 2 | 2 | delivered | 3 |
| BG1151 | 3 | 3 | delivered | 2 |
| BG1152 | 1 | 1 | delivered | 2 |
| BG1193 | 1 | 1 | delivered | 1 |
| BG1237 | 2 | 2 | delivered | 3 |
| BG1251 | 2 | 2 | delivered | 4 |
| BG1269 | 2 | 2 | delivered | 4 |
| BG1287 | 1 | 1 | delivered | 3 |
| BG1292 | 2 | 2 | delivered | 2 |
| BG1296 | 1 | 1 | delivered | 3 |
| BG1304 | 1 | 1 | delivered | 3 |
| BG1307 | 2 | 2 | delivered | 1 |
| BG1328 | 2 | 2 | delivered | 2 |
| BG1335 | 1 | 1 | delivered | 4 |
| BG1342 | 1 | 1 | delivered | 3 |
| BG1389 | 1 | 1 | delivered | 2 |
| BG1424 | 1 | 1 | delivered | 3 |
| BG1427 | 1 | 1 | delivered | 2 |
| BG1449 | 1 | 1 | delivered | 4 |
| BG1454 | 1 | 1 | delivered | 3 |
| BG1476 | 1 | 1 | delivered | 2 |
| BG1495 | 2 | 2 | delivered | 3 |
| BG1589 | 1 | 1 | delivered | 2 |
| BG1594 | 3 | 3 | delivered | 3 |
| BG1595 | 1 | 1 | delivered | 3 |
| BG1616 | 2 | 2 | delivered | 2 |
| BG1619 | 2 | 2 | delivered | 2 |
| BG1641 | 2 | 2 | delivered | 3 |
| BG1649 | 3 | 3 | delivered | 4 |
| BG1657 | 1 | 1 | delivered | 2 |
| BG1661 | 5 | 5 | delivered | 4 |
| BG1677 | 1 | 1 | delivered | 2 |
| BG1695 | 1 | 1 | delivered | 2 |
| BG1713 | 2 | 2 | delivered | 2 |
| BG1719 | 2 | 2 | delivered | 1 |
| BG1739 | 1 | 1 | delivered | 1 |
| BG1752 | 1 | 1 | added - the census guard refuses BG1304's two clock-bounded tests; every commit selecting it is red until fixed (run twenty-six); delivered | 1 |
| BG1282 | 1 | 1 | added - the goal is open bugs under fifty; five Lows filed from this run's reviews (BG1753-BG1757) left 50 open, so four groomed one-point Lows are fixed in the same run; delivered | 2 |
| BG1412 | 1 | 1 | added - the goal is open bugs under fifty; five Lows filed from this run's reviews (BG1753-BG1757) left 50 open, so four groomed one-point Lows are fixed in the same run; delivered | 1 |
| BG1497 | 1 | 1 | added - discharged carried at the review cap: BG1758; delivered | 3 |
| BG1504 | 1 | 1 | added - the goal is open bugs under fifty; five Lows filed from this run's reviews (BG1753-BG1757) left 50 open, so four groomed one-point Lows are fixed in the same run; delivered | 1 |

## Known issues handed over

5 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1753 | Low | A high-risk unit goes Fixed on one seat's round-two APPROVE after the second seat's REJECT - not-stop-ship, ruled by orchestrator |
| BG1754 | Low | A story moved to Blocked by decision defer --block stays Blocked after its last blocking decision is resolved - not-stop-ship, ruled by orchestrator |
| BG1755 | Low | The prose escaper spans a bare URL written straight against an author's code span so the two spans touch - not-stop-ship, ruled by orchestrator |
| BG1756 | Low | A plan refused for a criteria problem other than a missing Verify line names only the Affects and Points template - not-stop-ship, ruled by orchestrator |
| BG1757 | Low | A commit can stage a review-ledger row whose ruling cites a decision the commit does not carry - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-25T13:43:47Z | c13eb02cbd5f25dc |

Signing records the principal, the date and this report's fingerprint against RUN-01M87B5M.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | partial over 2 clause(s), 3 seat(s), no seat matched the author; achieved: Open bugs fall under fifty as forty-six Lows are fixed; partial: each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 46 leavable |
| batch | caller-check | 51 unit(s) of 51 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 33,117,619 |

Total 33,117,619, of which delegated 30,788,765. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (46 units); reviewer inherit (46 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $320.30 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $41.76 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 1106 subagent transcript(s); total agents 27, calls 4,535, priced 146,414,637. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 741 | 21,794,638 | 14.9% | 80.9% | 10.5% | 8.6% | 269,357 | 239,355 |
| builder | 7 | 2,439 | 85,000,932 | 58.1% | 62.9% | 26.3% | 10.8% | 15,361 | 226,464 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 1 | 62 | 826,283 | 0.6% | 62.7% | 16.2% | 21.1% | 15,535 | 85,259 |
| other | 18 | 1,293 | 38,792,784 | 26.5% | 49.8% | 33.7% | 16.5% | 60,375 | 157,583 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45617494659/45580894480/45567297724/45461301954 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 17h 53m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 34 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45617494659/45580894480/45567297724/45461301954 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45617494659/45580894480/45567297724/45461301954 - no push-triggered run on main concluded failure |

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

2 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is the closing clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

18 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | graduating (CR0751) | 0 | 2 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-011 | widen-after-brief | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 13 | 99 |
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
