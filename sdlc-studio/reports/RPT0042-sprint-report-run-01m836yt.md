# Sprint Report: RUN-01M836YT

## Goal

Release cut, filer, validate, refine and the carried units lose 25 Medium bugs; each fix's test fails without it

**Verdict: Judged partial** - 24 of the 25 planned Medium bugs fixed, each on an independent APPROVE with a test that fails without the fix; BG0967 (Medium) did not converge in three rounds and is carried under BG1723 for a rule-based redesign in run twenty-four

> **Run:** 2026-11-23T03:19:06Z to 2026-11-23T18:12:41Z (14.9h)
> **Verified on:** b0f51969cf365ce817d8e806ae6f54e2ce3d57fa   **Fingerprint:** d84571dc94cb9a92

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 80 | 80 | 1.0x | 30 of 30 delivered unit(s) |
| Minutes | 467.1 | 2190.8 | 4.69x | measured active minutes (spans or agent minutes) against their forecast, over the 30 of 30 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 1112.0 | 893.6 | 0.8x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0037, RPT0038, RPT0039, RPT0040, RPT0041), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 84,977,040 | 121,983,326 | 1.44x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 22,068,746 (input 9,986 x1, output 4,487,347 x5, cache write 5m 16,513,191 x1.25, cache write 1h 1,058,222 x2, cache read 767,786,718 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0151, RETRO0152, RETRO0153, RETRO0154, RETRO0155) |
| Tokens | 14,900,160 | 22,068,746 | 1.48x | the whole run: forecast over 30 of 30 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 62 delegated total(s) supplied are not added |
| Priced per point | 1,062,213 | 1,524,792 | 1.44x | the Priced cost row over the 80 point(s) of the 30 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0151, RETRO0152, RETRO0153, RETRO0154, RETRO0155) |
| Dollar cost | $339.91 | $333.81 | 0.98x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $4.25 | $4.17 | 0.98x | the Dollar cost row over the 80 point(s) of the 30 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG0948 | $9.77 estimated | 17.5 | 169.7 agent minutes, split by points | 558,756 | 804,894 agent tokens, split by points | 3,446,641 priced, split by points |
| BG0959 | $6.48 estimated | 11.7 | 60.8 agent minutes, split by points | 372,504 | 420,154 agent tokens, split by points | 2,406,605 priced, split by points |
| BG0968 | $2.51 estimated | 5.8 | 24.5 agent minutes, split by points | 186,252 | 160,909 agent tokens, split by points | 953,925 priced, split by points |
| BG0995 | $3.80 estimated | 5.8 | 37.0 agent minutes, split by points | 186,252 | 203,887 agent tokens, split by points | 1,474,658 priced, split by points |
| BG0997 | $9.38 estimated | 11.7 | 95.2 agent minutes, split by points | 372,504 | 576,792 agent tokens, split by points | 3,541,638 priced, split by points |
| BG1417 | $5.01 estimated | 11.7 | 48.9 agent minutes, split by points | 372,504 | 321,817 agent tokens, split by points | 1,907,850 priced, split by points |
| BG1452 | $7.59 estimated | 11.7 | 74.1 agent minutes, split by points | 372,504 | 407,774 agent tokens, split by points | 2,949,316 priced, split by points |
| BG1475 | $2.25 estimated | 17.5 | 38.7 agent minutes, split by points | 558,756 | 125,151 agent tokens, split by points | 812,015 priced, split by points |
| BG1510 | $6.83 estimated | 11.7 | 60.4 agent minutes, split by points | 372,504 | 506,681 agent tokens, split by points | 2,443,361 priced, split by points |
| BG1532 | $1.02 estimated | 29.2 | 17.2 agent minutes, split by points | 931,260 | 98,002 agent tokens, split by points | 325,490 priced, split by points |
| BG1537 | $9.77 estimated | 17.5 | 169.7 agent minutes, split by points | 558,756 | 804,893 agent tokens, split by points | 3,446,641 priced, split by points |
| BG1541 | $7.43 estimated | 17.5 | 67.7 agent minutes, split by points | 558,756 | 295,886 agent tokens, split by points | 3,024,969 priced, split by points |
| BG1542 | $5.40 estimated | 11.7 | 51.8 agent minutes, split by points | 372,504 | 420,139 agent tokens, split by points | 1,929,379 priced, split by points |
| BG1544 | $5.40 estimated | 11.7 | 51.8 agent minutes, split by points | 372,504 | 420,138 agent tokens, split by points | 1,929,378 priced, split by points |
| BG1545 | $10.25 estimated | 17.5 | 90.6 agent minutes, split by points | 558,756 | 760,021 agent tokens, split by points | 3,665,041 priced, split by points |
| BG1549 | $9.82 estimated | 11.7 | 88.7 agent minutes, split by points | 372,504 | 740,907 agent tokens, split by points | 3,308,466 priced, split by points |
| BG1550 | $9.82 estimated | 11.7 | 88.7 agent minutes, split by points | 372,504 | 740,906 agent tokens, split by points | 3,308,465 priced, split by points |
| BG1551 | $11.39 estimated | 17.5 | 111.1 agent minutes, split by points | 558,756 | 611,662 agent tokens, split by points | 4,423,974 priced, split by points |
| BG1552 | $15.28 estimated | 17.5 | 147.4 agent minutes, 2 of 3 agent totals split by points | 558,756 | 822,641 agent tokens, 2 of 3 agent totals split by points | 5,851,923 priced, 2 of 3 agent totals split by points |
| BG1567 | $6.42 estimated | 17.5 | 57.6 agent minutes, split by points | 558,756 | 228,836 agent tokens, split by points | 2,670,881 priced, split by points |
| BG1625 | $1.54 estimated | 29.2 | 56.2 agent minutes, split by points | 931,260 | 138,130 agent tokens, split by points | 629,127 priced, split by points |
| BG1707 | $2.25 estimated | 17.5 | 38.7 agent minutes, split by points | 558,756 | 125,151 agent tokens, split by points | 812,015 priced, split by points |
| BG1714 | $1.02 estimated | 29.2 | 17.2 agent minutes, split by points | 931,260 | 98,002 agent tokens, split by points | 325,489 priced, split by points |
| BG1717 | $1.54 estimated | 29.2 | 56.2 agent minutes, split by points | 931,260 | 138,128 agent tokens, split by points | 629,125 priced, split by points |
| US1324 | $7.43 estimated | 17.5 | 67.7 agent minutes, split by points | 558,756 | 295,885 agent tokens, split by points | 3,024,968 priced, split by points |
| US1326 | $13.49 estimated | 17.5 | 146.6 agent minutes | 558,756 | 1,105,411 agent tokens | 4,481,400 priced |
| BG0974 | $11.59 estimated | 11.7 | 106.4 agent minutes, split by points | 372,504 | 569,437 agent tokens, split by points | 4,256,305 priced, split by points |
| BG1718 | $2.48 estimated | 5.8 | 22.6 agent minutes, split by points | 186,252 | 98,628 agent tokens, split by points | 1,008,323 priced, split by points |
| BG1694 | $6.83 estimated | 11.7 | 90.1 agent minutes | 372,504 | 544,410 agent tokens | 2,154,296 priced |
| BG1730 | $2.87 estimated | 11.7 | 37.2 agent minutes | 372,504 | 205,999 agent tokens | 943,688 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 29 | 78 |
| Delivered of the plan | 28 | 76 |
| Added mid-run and delivered | 2 of 2 added | 4 |
| Dropped | 1 | 2 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 80.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0948 | 3 | 3 | delivered | 2 |
| BG0959 | 2 | 2 | delivered | 2 |
| BG0967 | 2 | 2 | dropped - carried at the review cap: BG1723 | 3 |
| BG0968 | 1 | 1 | delivered | 1 |
| BG0995 | 1 | 1 | delivered | 2 |
| BG0997 | 2 | 2 | delivered | 3 |
| BG1417 | 2 | 2 | delivered | 1 |
| BG1452 | 2 | 2 | delivered | 2 |
| BG1475 | 3 | 3 | delivered | 1 |
| BG1510 | 2 | 2 | delivered | 2 |
| BG1532 | 5 | 5 | delivered | 1 |
| BG1537 | 3 | 3 | delivered | 2 |
| BG1541 | 3 | 3 | delivered | 2 |
| BG1542 | 2 | 2 | delivered | 1 |
| BG1544 | 2 | 2 | delivered | 1 |
| BG1545 | 3 | 3 | delivered | 2 |
| BG1549 | 2 | 2 | delivered | 3 |
| BG1550 | 2 | 2 | delivered | 3 |
| BG1551 | 3 | 3 | delivered | 2 |
| BG1552 | 3 | 3 | delivered | 3 |
| BG1567 | 3 | 3 | delivered | 1 |
| BG1625 | 5 | 5 | delivered | 2 |
| BG1707 | 3 | 3 | delivered | 1 |
| BG1714 | 5 | 5 | delivered | 1 |
| BG1717 | 5 | 5 | delivered | 2 |
| US1324 | 3 | 3 | delivered | 2 |
| US1326 | 3 | 3 | delivered | 5 |
| BG0974 | 2 | 2 | delivered | 3 |
| BG1718 | 1 | 1 | delivered | 2 |
| BG1694 | 2 | 2 | added - round three approved under D0606; the carry BG1727 is Fixed; delivered | 3 |
| BG1730 | 2 | 2 | added - found by the scheduled corpus-verify run 45196238545: a shared test module name reddens US0253 AC2, which a release gate's executing verify refuses; a 2-point rename and census guard, built beside US1326's last repair; delivered | 2 |

## Known issues handed over

5 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1723 | Medium | BG0967 did not converge in review: round 2 REJECT findings - deferred, ruled by orchestrator |
| BG1719 | Low | artifact.py new and batch, and the Low-finding consolidator, write a title's bare snake_case identifier into the H1 and the index row, so markdownlint refuses the file - not-stop-ship, ruled by orchestrator |
| BG1722 | Low | `conformance.adopt_after` takes a schema v3 cutoff on a schema v2 project, so the conformance lane exempts every sequential unit - not-stop-ship, ruled by orchestrator |
| BG1726 | Low | readiness detector-owed reports a project lens as PRD (None) and would declare a bare pack directory as the owed unit's Affects - not-stop-ship, ruled by orchestrator |
| BG1731 | Low | US1112 AC4 reads red in CI: a batched node over its per-verifier ceiling is also spawned on its own - deferred, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M836YT.

## Appendix

### Goal judgement

What the close judged against the sprint goal: the goal panel's verdict, each open defect ruled
blocking with its reason, the count of blocking and leavable defects, and the caller-check. The
close refuses on none of them; they are here for the signer to weigh.

| Item | Ruling | Detail |
| --- | --- | --- |
| sprint goal | goal panel | UNANSWERED over 2 clause(s), 3 seat(s), no seat matched the author; UNANSWERED (3 seat(s) silent): Release cut, filer, validate, refine and the carried units lose 25 Medium bugs; UNANSWERED (3 seat(s) silent): each fix's test fails without it |
| open defects | defects vs goal | 0 BLOCKING, 272 leavable |
| batch | caller-check | 30 unit(s) of 30 ship a mechanism with no named caller |

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 22,068,746 |

Total 22,068,746, of which delegated 13,360,709. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (29 units); reviewer inherit (29 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $333.24 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $0.5683 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 1007 subagent transcript(s); total agents 45, calls 4,785, priced 121,983,326. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 657 | 20,768,631 | 17.0% | 81.0% | 10.2% | 8.8% | 230,587 | 257,716 |
| builder | 13 | 1,915 | 49,456,984 | 40.5% | 64.9% | 17.8% | 17.3% | 15,360 | 171,268 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 17 | 1,246 | 26,884,673 | 22.0% | 60.2% | 15.2% | 24.5% | 15,652 | 132,596 |
| other | 14 | 967 | 24,873,037 | 20.4% | 46.9% | 31.1% | 22.0% | 15,370 | 127,049 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 45231169958/45204295387/45157639673/45107578561 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 13h 56m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 45 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 45231169958/45204295387/45157639673/45107578561 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 45231169958/45204295387/45157639673/45107578561 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 9 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 2 | 0 | 2 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

10 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 1 |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-011 | widen-after-brief | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 9 | 79 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
| LC-022 | hand-in outside the lane folder | active | 0 | 0 |
| LC-023 | census missed by a narrow commit | active | 0 | 0 |
| LC-024 | second seat past the joint cap | active | 0 | 0 |
