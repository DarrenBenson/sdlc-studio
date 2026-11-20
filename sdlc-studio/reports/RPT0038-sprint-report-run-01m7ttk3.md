# Sprint Report: RUN-01M7TTK3

## Goal

PyYAML is required and checked at install, the installer fails safe, and the TRD and PRD describe the shipped code.

**Verdict: Judged achieved** - All 34 units closed with an independent review: the installers and the gate refuse a machine without PyYAML and name how to install it, the config reader refuses rather than reading defaults, both installers refuse to delete or replace a folder that is not an SDLC Studio install and refuse an unverified download, and the PRD and TRD statements this run's units named now match the shipped code, each held by a test. The leftovers are Low test-strength gaps (BG1637, BG1639, BG1643) and one traceback in place of a refusal (BG1642), each filed and ruled not-stop-ship.

> **Run:** 2026-11-19T21:06:22Z to 2026-11-20T04:29:53Z (7.4h)
> **Verified on:** b851ab1b7505a186e11f66bd0406ab5b1faffaa7   **Fingerprint:** 5218da07956fd93a

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 68 | 68 | 1.0x | 34 of 34 delivered unit(s) |
| Minutes | 385.3 | 4594.7 | 11.92x | measured active minutes (spans or agent minutes) against their forecast, over the 33 of 34 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 706.5 | 443.5 | 0.63x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0033, RPT0034, RPT0035, RPT0036, RPT0037), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 51,864,008 | 54,390,408 | 1.05x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 8,808,209 (input 4,982 x1, output 2,057,541 x5, cache write 5m 6,161,018 x1.25, cache write 1h 584,668 x2, cache read 352,271,129 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0147, RETRO0148, RETRO0149, RETRO0150, RETRO0151) |
| Tokens | 12,665,136 | 8,808,209 | 0.7x | the whole run: forecast over 34 of 34 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 42 delegated total(s) supplied are not added |
| Priced per point | 762,706 | 799,859 | 1.05x | the Priced cost row over the 68 point(s) of the 34 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0147, RETRO0148, RETRO0149, RETRO0150, RETRO0151) |
| Dollar cost | $207.46 | $139.29 | 0.67x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.05 | $2.05 | 0.67x | the Dollar cost row over the 68 point(s) of the 34 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1516 | $3.45 estimated | 17.5 | 253.1 | 558,756 | 180,835 agent tokens, split by points | 1,560,007 priced, split by points |
| BG1517 | $2.30 estimated | 11.7 | 253.4 | 372,504 | 120,558 agent tokens, split by points | 1,040,006 priced, split by points |
| BG1525 | $2.41 estimated | 11.7 | 213.4 | 372,504 | 156,473 agent tokens, split by points | 1,143,481 priced, split by points |
| BG1526 | $0.3336 estimated | 5.8 | 97.2 | 186,252 | 26,430 agent tokens, split by points | 267,749 priced, split by points |
| BG1527 | $0.3336 estimated | 5.8 | 98.9 | 186,252 | 26,430 agent tokens, split by points | 267,749 priced, split by points |
| BG1528 | $0.3336 estimated | 5.8 | 113.1 | 186,252 | 26,430 agent tokens, split by points | 267,749 priced, split by points |
| BG1529 | $0.3548 estimated | 11.7 | 95.4 | 372,504 | 37,734 agent tokens, split by points | 269,414 priced, split by points |
| BG1530 | $0.3548 estimated | 11.7 | 119.8 | 372,504 | 37,734 agent tokens, split by points | 269,413 priced, split by points |
| BG1531 | $3.45 estimated | 17.5 | 327.7 | 558,756 | 180,835 agent tokens, split by points | 1,560,007 priced, split by points |
| BG1533 | $0.3548 estimated | 11.7 | 120.7 | 372,504 | 37,734 agent tokens, split by points | 269,413 priced, split by points |
| BG1543 | $4.46 estimated | 17.5 | 210.0 | 558,756 | 279,102 agent tokens, split by points | 1,579,997 priced, split by points |
| BG1546 | $2.47 estimated | 17.5 | 129.5 | 558,756 | 152,819 agent tokens, split by points | 910,285 priced, split by points |
| BG1547 | $1.64 estimated | 11.7 | 131.3 | 372,504 | 101,880 agent tokens, split by points | 606,857 priced, split by points |
| US1296 | $2.47 estimated | 17.5 | 141.0 | 558,756 | 152,819 agent tokens, split by points | 910,285 priced, split by points |
| US1297 | $9.29 estimated | 29.2 | 138.6 | 931,260 | 835,148 agent tokens | 3,212,832 priced |
| US1298 | $3.23 estimated | 17.5 | 181.2 | 558,756 | 275,617 agent tokens, split by points | 1,087,882 priced, split by points |
| US1299 | $4.00 estimated | 11.7 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 231,665 agent tokens, 1 of 2 agent totals split by points | 1,403,530 priced, 1 of 2 agent totals split by points |
| BG1096 | $0.9715 estimated | 5.8 | 142.3 | 186,252 | 41,412 agent tokens, split by points | 385,296 priced, split by points |
| BG1162 | $0.6672 estimated | 11.7 | 116.8 | 372,504 | 52,860 agent tokens, split by points | 535,497 priced, split by points |
| BG1168 | $0.6672 estimated | 11.7 | 118.8 | 372,504 | 52,859 agent tokens, split by points | 535,497 priced, split by points |
| BG1180 | $1.20 estimated | 5.8 | 219.1 | 186,252 | 78,236 agent tokens, split by points | 571,741 priced, split by points |
| BG1553 | $2.41 estimated | 11.7 | 221.5 | 372,504 | 156,471 agent tokens, split by points | 1,143,480 priced, split by points |
| BG1554 | $0.3336 estimated | 5.8 | 103.7 | 186,252 | 26,430 agent tokens, split by points | 267,748 priced, split by points |
| BG1555 | $0.6672 estimated | 11.7 | 105.1 | 372,504 | 52,859 agent tokens, split by points | 535,497 priced, split by points |
| BG1556 | $1.94 estimated | 11.7 | 142.6 | 372,504 | 82,824 agent tokens, split by points | 770,592 priced, split by points |
| BG1557 | $1.94 estimated | 11.7 | 143.1 | 372,504 | 82,824 agent tokens, split by points | 770,592 priced, split by points |
| BG1565 | $1.94 estimated | 11.7 | 147.1 | 372,504 | 82,824 agent tokens, split by points | 770,591 priced, split by points |
| BG1621 | $0.9715 estimated | 5.8 | 147.7 | 186,252 | 41,412 agent tokens, split by points | 385,296 priced, split by points |
| BG1631 | $1.64 estimated | 11.7 | 83.4 | 372,504 | 101,880 agent tokens, split by points | 606,857 priced, split by points |
| BG1632 | $1.64 estimated | 11.7 | 84.5 | 372,504 | 101,880 agent tokens, split by points | 606,857 priced, split by points |
| BG1633 | $2.15 estimated | 11.7 | 121.1 | 372,504 | 183,745 agent tokens, split by points | 725,255 priced, split by points |
| BG1634 | $1.33 estimated | 11.7 | 40.1 | 372,504 | 84,189 agent tokens, split by points | 446,475 priced, split by points |
| BG1644 | $1.09 estimated | 5.8 | 12.2 | 186,252 | 89,171 agent tokens | 331,262 priced |
| BG1647 | $1.37 estimated | 5.8 | 21.4 | 186,252 | 99,237 agent tokens | 447,432 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 28 | 58 |
| Delivered of the plan | 28 | 58 |
| Added mid-run and delivered | 6 of 6 added | 10 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 68.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1516 | 3 | 3 | delivered | 2 |
| BG1517 | 2 | 2 | delivered | 2 |
| BG1525 | 2 | 2 | delivered | 2 |
| BG1526 | 1 | 1 | delivered | 1 |
| BG1527 | 1 | 1 | delivered | 1 |
| BG1528 | 1 | 1 | delivered | 1 |
| BG1529 | 2 | 2 | delivered | 1 |
| BG1530 | 2 | 2 | delivered | 1 |
| BG1531 | 3 | 3 | delivered | 2 |
| BG1533 | 2 | 2 | delivered | 1 |
| BG1543 | 3 | 3 | delivered | 2 |
| BG1546 | 3 | 3 | delivered | 1 |
| BG1547 | 2 | 2 | delivered | 1 |
| US1296 | 3 | 3 | delivered | 1 |
| US1297 | 5 | 5 | delivered | 1 |
| US1298 | 3 | 3 | delivered | 2 |
| US1299 | 2 | 2 | delivered | 2 |
| BG1096 | 1 | 1 | delivered | 1 |
| BG1162 | 2 | 2 | delivered | 1 |
| BG1168 | 2 | 2 | delivered | 1 |
| BG1180 | 1 | 1 | delivered | 2 |
| BG1553 | 2 | 2 | delivered | 2 |
| BG1554 | 1 | 1 | delivered | 1 |
| BG1555 | 2 | 2 | delivered | 1 |
| BG1556 | 2 | 2 | delivered | 1 |
| BG1557 | 2 | 2 | delivered | 1 |
| BG1565 | 2 | 2 | delivered | 1 |
| BG1621 | 1 | 1 | delivered | 1 |
| BG1631 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1632 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1633 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1634 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1644 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1647 | 1 | 1 | added - no reason recorded; delivered | 1 |

## Known issues handed over

12 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1635 | Low | The installer tests' source reads accept dead or inverted install.ps1 guards - not-stop-ship, ruled by orchestrator |
| BG1636 | Low | Installer tests that run install.sh on PATH=/usr/bin:/bin fail where the system python3 cannot import yaml - not-stop-ship, ruled by orchestrator |
| BG1637 | Low | gate.py's PyYAML refusal says a config is read as defaults, and its release and json routes are unpinned - not-stop-ship, ruled by orchestrator |
| BG1638 | Low | config-defaults.yaml still calls two_backlog.enforce the one gate-bearing key that ships off - not-stop-ship, ruled by orchestrator |
| BG1639 | Low | The PRD drift checkers accept rewordings of the claims they exist to refuse - not-stop-ship, ruled by orchestrator |
| BG1640 | Low | install.sh's sidecar refusals for an empty body, a transport fault and wget are unpinned - not-stop-ship, ruled by orchestrator |
| BG1641 | Low | A repair's QA brief does not name the reviewer whose REJECT it answers, so a fresh reviewer's round two is refused at record - not-stop-ship, ruled by orchestrator |
| BG1642 | Low | config.py show prints a RuntimeError traceback without PyYAML instead of the one-line refusal - not-stop-ship, ruled by orchestrator |
| BG1643 | Low | The TRD checks left by run nineteen's TRD repairs accept rewordings and leave three claims unpinned - not-stop-ship, ruled by orchestrator |
| BG1645 | Low | Two more verify_ac lint tests judge the live help/ directory, so a non-markdown file there turns them red - not-stop-ship, ruled by orchestrator |
| BG1646 | Low | The PRD changelog-row check reads committed history, so a commit that changes the PRD without a row passes its own hooks - not-stop-ship, ruled by orchestrator |
| BG1648 | Low | A test leaves a second verify_ac module in sys.modules, so later tests patch an object the code no longer imports - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-20T04:41:08Z | 5218da07956fd93a |

Signing records the principal, the date and this report's fingerprint against RUN-01M7TTK3.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 8,808,209 |

Total 8,808,209, of which delegated 4,271,356. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (34 units); reviewer inherit (34 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $131.46 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $7.82 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 790 subagent transcript(s); total agents 29, calls 2,400, priced 54,390,408. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 404 | 12,637,476 | 23.2% | 83.1% | 9.3% | 7.6% | 261,922 | 261,449 |
| builder | 7 | 720 | 16,258,213 | 29.9% | 63.3% | 17.6% | 19.1% | 14,469 | 146,170 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 4 | 443 | 10,204,408 | 18.8% | 66.6% | 11.1% | 22.2% | 14,829 | 155,538 |
| other | 17 | 833 | 15,290,312 | 28.1% | 49.9% | 24.3% | 25.8% | 14,936 | 95,139 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 1 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44662051182 - 1 push-triggered run(s) on main in the run window |
| Lead time for changes | 6h 27m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 12 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44662051182 - 1 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44662051182 - no push-triggered run on main concluded failure |

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
| gate | 1 | 0 | 1 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 6 | 54 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
