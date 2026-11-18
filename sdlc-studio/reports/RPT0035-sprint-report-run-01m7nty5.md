# Sprint Report: RUN-01M7NTY5

## Goal

No gate passes work it never judged, and a run closed in the operator's absence awaits a trustworthy signature

**Verdict: Judged partial** - Every gate the audit named now refuses work it never judged, and a run closed in the operator's absence awaits a signature that must name its authority; BG1582 leaves one sign path (HEAD past the close commit, no later run open) that skips the whole-tree check, deferred to the operator

> **Run:** 2026-11-17T22:31:56Z to 2026-11-18T10:24:52Z (11.9h)
> **Verified on:** 9925e144c49e17f3230185f466990eeb4825b1f8   **Fingerprint:** a9daaca50ef063ce

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 51 | 51 | 1.0x | 17 of 17 delivered unit(s) |
| Minutes | 297.6 | 3913.2 | 13.15x | measured active minutes (spans or agent minutes) against their forecast, over the 17 of 17 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 477.6 | 712.9 | 1.49x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0030, RPT0031, RPT0032, RPT0033, RPT0034), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 43,013,349 | 37,312,667 | 0.87x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 6,047,041 (input 3,634 x1, output 1,535,899 x5, cache write 5m 4,004,493 x1.25, cache write 1h 503,015 x2, cache read 236,178,922 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0144, RETRO0145, RETRO0146, RETRO0147, RETRO0148) |
| Tokens | 9,498,852 | 6,047,041 | 0.64x | the whole run: forecast over 17 of 17 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 22 delegated total(s) supplied are not added |
| Priced per point | 843,399 | 731,621 | 0.87x | the Priced cost row over the 51 point(s) of the 17 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0144, RETRO0145, RETRO0146, RETRO0147, RETRO0148) |
| Dollar cost | $172.05 | $102.01 | 0.59x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.37 | $2.00 | 0.59x | the Dollar cost row over the 51 point(s) of the 17 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1507 | $3.75 estimated | 17.5 | 292.2 | 558,756 | 173,247 agent tokens, split by points | 1,441,671 priced, split by points |
| BG1518 | $2.59 estimated | 17.5 | 209.3 | 558,756 | 168,256 agent tokens | 873,560 priced |
| BG1519 | $7.43 estimated | 29.2 | 247.7 | 931,260 | 484,598 agent tokens, 1 of 2 agent totals split by points | 2,661,926 priced, 1 of 2 agent totals split by points |
| BG1520 | $6.25 estimated | 29.2 | 292.9 | 931,260 | 288,745 agent tokens, split by points | 2,402,785 priced, split by points |
| BG1521 | $2.96 estimated | 17.5 | 184.7 | 558,756 | 192,183 agent tokens, split by points | 1,093,086 priced, split by points |
| BG1522 | $2.96 estimated | 17.5 | 185.0 | 558,756 | 192,183 agent tokens, split by points | 1,093,086 priced, split by points |
| BG1523 | $2.10 estimated | 17.5 | 125.9 | 558,756 | 145,064 agent tokens | 697,915 priced |
| BG1524 | $2.38 estimated | 29.2 | 107.1 | 931,260 | 162,619 agent tokens, split by points | 796,550 priced, split by points |
| US1290 | $6.25 estimated | 29.2 | 289.7 | 931,260 | 288,745 agent tokens, split by points | 2,402,786 priced, split by points |
| US1291 | $2.01 estimated | 17.5 | 207.3 | 558,756 | 86,348 agent tokens, split by points | 791,903 priced, split by points |
| US1292 | $1.43 estimated | 17.5 | 108.6 | 558,756 | 97,571 agent tokens, split by points | 477,930 priced, split by points |
| US1293 | $4.37 estimated | 11.7 | 297.3 | 372,504 | 304,137 agent tokens | 1,467,394 priced |
| US1313 | $1.70 estimated | 11.7 | 607.9 | 372,504 | 122,368 agent tokens | 561,034 priced |
| US1314 | $3.44 estimated | 17.5 | 82.9 | 558,756 | 302,694 agent tokens | 1,122,874 priced |
| BG1579 | $0.5407 estimated | 5.8 | 329.4 | 186,252 | 45,517 agent tokens, split by points | 166,701 priced, split by points |
| BG1580 | $0.5407 estimated | 5.8 | 330.0 | 186,252 | 45,517 agent tokens, split by points | 166,701 priced, split by points |
| BG1586 | $0.5977 estimated | 5.8 | 15.5 | 186,252 | 54,891 agent tokens | 180,670 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 14 | 48 |
| Delivered of the plan | 14 | 48 |
| Added mid-run and delivered | 3 of 3 added | 3 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 51.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1507 | 3 | 3 | delivered | 2 |
| BG1518 | 3 | 3 | delivered | 1 |
| BG1519 | 5 | 5 | delivered | 2 |
| BG1520 | 5 | 5 | delivered | 2 |
| BG1521 | 3 | 3 | delivered | 1 |
| BG1522 | 3 | 3 | delivered | 1 |
| BG1523 | 3 | 3 | delivered | 1 |
| BG1524 | 5 | 5 | delivered | 1 |
| US1290 | 5 | 5 | delivered | 2 |
| US1291 | 3 | 3 | delivered | 1 |
| US1292 | 3 | 3 | delivered | 1 |
| US1293 | 2 | 2 | delivered | 2 |
| US1313 | 2 | 2 | delivered | 1 |
| US1314 | 3 | 3 | delivered | 1 |
| BG1579 | 1 | 1 | added - push-boundary regression from this run's units (D0525); delivered | 1 |
| BG1580 | 1 | 1 | added - push-boundary regression from this run's units (D0525); delivered | 1 |
| BG1586 | 1 | 1 | added - D0526: the push boundary refused 4ed7d225 on US1313's undeclared hand-maintained script list; delivered | 1 |

## Known issues handed over

17 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1570 | Medium | The evidence pack trusts the run record as committed at the build revision, so one commit that edits a report's figures, its signature and its run record together still passes |
| BG1574 | Medium | No gate refuses a unit's commit that ships no changelog fragment, so run sixteen landed twelve of fourteen units without one - not-stop-ship, ruled by orchestrator |
| BG1578 | Medium | The weekly corpus verify of 2026-11-16 read US0926 AC1 and US0996 AC3 red on CI, and both pass locally at HEAD - not-stop-ship, ruled by orchestrator |
| BG1581 | Medium | test_a_refused_message_never_reaches_the_unit_suites fails by 4 ms on the gate host under the nested unittest run, refusing a push - not-stop-ship, ruled by orchestrator |
| BG1582 | Medium | Once HEAD moves past the close commit, sprint sign skips the whole-tree check, so an uncommitted edit to a unit's file seals with no later run open - deferred, ruled by orchestrator |
| CR0740 | Medium | Prevent or retire lesson LC-021 (lane paperwork the landing refuses) |
| BG1571 | Low | US1314's tests never pin a raise to a middle class, a story with several Affects files, the open-status scope, or the silent skip of a stamp apply cannot rewrite |
| BG1572 | Low | The evidence pack crashes with a traceback on a malformed report instead of refusing it by name |
| BG1573 | Low | The second-seat refusal past the round cap names a seat that does not exist when the reviewer id carries no seat word |
| BG1575 | Low | BG0660's unscoped-boundary guard flags a --run-tests call that runs no other lane, and is satisfied by an --only that call ignores |
| BG1576 | Low | The skill-tests lane's serial_only collection may read empty under an inherited -q, so serial tests could be skipped unseen |
| BG1577 | Low | The TSD's full-suite row states BG1519's count floor but not that a commit whose selection holds only push-deferred tests is exempt |
| BG1583 | Low | sprint sign names the wrong page when the later run has also closed, and three of US1290's guards have no test - not-stop-ship, ruled by orchestrator |
| BG1584 | Low | BG1507 and BG1520 left four checks with no test: --includes, includeIf identities, the self-check-author refusal and the retro's owed branches - not-stop-ship, ruled by orchestrator |
| BG1585 | Low | The pre-commit gate lane passes the whole reconcile detect JSON through one environment variable, so on a large corpus it dies with Argument list too long and never prints the drift detail - not-stop-ship, ruled by orchestrator |
| BG1587 | Low | A commit that adds a test file never selects test_test_census.py, whose guards scan every test file, so a new hand-copied script list is first seen by the full suite at push - not-stop-ship, ruled by orchestrator |
| BG1588 | Low | The hand-copied-list guard misses _KNOWN_MIRRORS growing and exempts a whole file on one marker, and BG1586's AC2 cannot tell a marker with no reason - not-stop-ship, ruled by orchestrator |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 8 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0528) | 2026-11-18T15:16:02Z | a9daaca50ef063ce |

Signing records the principal, the date and this report's fingerprint against RUN-01M7NTY5.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 6,047,041 |

Total 6,047,041, of which delegated 3,154,683. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (14 units); reviewer inherit (14 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $102.01 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 696 subagent transcript(s); total agents 26, calls 1,754, priced 37,312,667. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 329 | 8,958,495 | 24.0% | 78.6% | 11.2% | 10.2% | 297,934 | 215,538 |
| builder | 10 | 702 | 14,284,600 | 38.3% | 60.6% | 16.0% | 23.3% | 14,041 | 126,015 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 3 | 202 | 4,113,973 | 11.0% | 60.5% | 13.4% | 26.1% | 14,565 | 125,400 |
| other | 12 | 521 | 9,955,598 | 26.7% | 54.5% | 21.8% | 23.7% | 27,435 | 107,457 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44275353383/44193887066 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 10h 23m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 19 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44275353383/44193887066 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44275353383/44193887066 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 3 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 1 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 4 | 42 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 1 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 1 | 2 |
