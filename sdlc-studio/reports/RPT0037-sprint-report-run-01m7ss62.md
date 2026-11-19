# Sprint Report: RUN-01M7SS62

## Goal

Toward cost per unit: one drive step per hand-back, replayed machine-run mutants, configurable CI red-run rules, cost measured or flagged.

**Verdict: Judged achieved** - Every clause delivered on independent APPROVEs, all 15 units resolved: one drive step per hand-back (US1198, with US1192, US1193, US1195, US1196 and US1197 carrying the hand-back loop), replayed machine-run mutants (US1200, US1201, US1202), configurable CI red-run rules (US1236, US1237, US1238), and cost measured or flagged (BG1605, BG1607). Six units needed a repair round, and each repair answered every blocking finding of both seats. Known issues carried, none stop-ship: BG1623 and BG1626 (drive step's resumes and guards), BG1627 (an outer brief bound orphans the runner), BG1625 (report and replay edges).

> **Run:** 2026-11-19T11:34:33Z to 2026-11-19T19:51:52Z (8.3h)
> **Verified on:** a0e07099240f4620891b70a3c9ae4c03a3950c02   **Fingerprint:** 37a01f3d6c94675d

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 48 | 48 | 1.0x | 15 of 15 delivered unit(s) |
| Minutes | 105.1 | 1229.5 | 11.7x | measured active minutes (spans or agent minutes) against their forecast, over the 8 of 15 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 541.5 | 497.3 | 0.92x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0032, RPT0033, RPT0034, RPT0035, RPT0036), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 36,609,888 | 46,289,662 | 1.26x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 7,725,828 (input 3,862 x1, output 1,894,460 x5, cache write 5m 5,351,434 x1.25, cache write 1h 476,072 x2, cache read 291,720,636 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0146, RETRO0147, RETRO0148, RETRO0149, RETRO0150) |
| Tokens | 8,940,096 | 7,725,828 | 0.86x | the whole run: forecast over 15 of 15 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 22 delegated total(s) supplied are not added |
| Priced per point | 762,706 | 964,368 | 1.26x | the Priced cost row over the 48 point(s) of the 15 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0146, RETRO0147, RETRO0148, RETRO0149, RETRO0150) |
| Dollar cost | $146.44 | $126.81 | 0.87x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.05 | $2.64 | 0.87x | the Dollar cost row over the 48 point(s) of the 15 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1605 | $2.54 estimated | 11.7 | 186.7 | 372,504 | 185,439 agent tokens, split by points | 908,787 priced, split by points |
| BG1607 | $2.54 estimated | 11.7 | 192.7 | 372,504 | 185,438 agent tokens, split by points | 908,787 priced, split by points |
| US1192 | $7.27 estimated | 29.2 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 931,260 | 609,034 agent tokens, 1 of 2 agent totals split by points | 2,403,512 priced, 1 of 2 agent totals split by points |
| US1193 | $2.81 estimated | 17.5 | 193.1 | 558,756 | 213,544 agent tokens, split by points | 949,792 priced, split by points |
| US1195 | $3.82 estimated | 17.5 | 194.3 | 558,756 | 278,158 agent tokens, split by points | 1,363,181 priced, split by points |
| US1196 | $6.12 estimated | 29.2 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 931,260 | 318,150 agent tokens, split by points | 2,256,442 priced, split by points |
| US1197 | $3.67 estimated | 17.5 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 558,756 | 190,891 agent tokens, split by points | 1,353,865 priced, split by points |
| US1198 | $6.12 estimated | 29.2 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 931,260 | 318,150 agent tokens, split by points | 2,256,441 priced, split by points |
| US1200 | $4.16 estimated | 17.5 | 189.2 | 558,756 | 238,352 agent tokens | 1,475,599 priced |
| US1201 | $10.68 estimated | 29.2 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 931,260 | 661,994 agent tokens, split by points | 3,913,694 priced, split by points |
| US1202 | $4.27 estimated | 11.7 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 264,798 agent tokens, split by points | 1,565,478 priced, split by points |
| US1236 | $1.44 estimated | 11.7 | 104.1 | 372,504 | 75,735 agent tokens, split by points | 528,736 priced, split by points |
| US1237 | $1.44 estimated | 11.7 | 104.3 | 372,504 | 75,735 agent tokens, split by points | 528,736 priced, split by points |
| US1238 | $5.59 estimated | 29.2 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 931,260 | 328,068 agent tokens, 1 of 2 agent totals split by points | 1,968,814 priced, 1 of 2 agent totals split by points |
| BG1622 | $1.38 estimated | 5.8 | 65.1 | 186,252 | 102,423 agent tokens | 443,589 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 14 | 47 |
| Delivered of the plan | 14 | 47 |
| Added mid-run and delivered | 1 of 1 added | 1 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 48.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1605 | 2 | 2 | delivered | 2 |
| BG1607 | 2 | 2 | delivered | 2 |
| US1192 | 5 | 5 | delivered | 2 |
| US1193 | 3 | 3 | delivered | 1 |
| US1195 | 3 | 3 | delivered | 2 |
| US1196 | 5 | 5 | delivered | 2 |
| US1197 | 3 | 3 | delivered | 2 |
| US1198 | 5 | 5 | delivered | 2 |
| US1200 | 3 | 3 | delivered | 1 |
| US1201 | 5 | 5 | delivered | 2 |
| US1202 | 2 | 2 | delivered | 2 |
| US1236 | 2 | 2 | delivered | 1 |
| US1237 | 2 | 2 | delivered | 1 |
| US1238 | 5 | 5 | delivered | 2 |
| BG1622 | 1 | 1 | added - no reason recorded; delivered | 1 |

## Known issues handed over

22 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1609 | Medium | A high-risk unit's second review seat defaults to engineering, the seat that built it, so the engineering brief's printed record command is a self-review - not-stop-ship, ruled by orchestrator |
| BG1610 | Medium | lane land's commit timeout kills git but leaves the hooks' test run running orphaned, holding the host's CPU after the land reports nothing committed - not-stop-ship, ruled by orchestrator |
| BG1614 | Medium | lane accept records a second seat's verdict against the unit's saved qa brief, not the brief the verdict file names - not-stop-ship, ruled by orchestrator |
| BG1623 | Medium | sprint drive and drive step: an oversized brief exits 2 after work ran, a refused paperwork commit re-runs to exit 0, any agent id is accepted as the reviewer, and several guards have no test - not-stop-ship, ruled by orchestrator |
| BG1624 | Medium | Flaky: test_lane_run's timed-out git add test can find index.lock left behind on the gate host - not-stop-ship, ruled by orchestrator |
| BG1625 | Medium | The recorded runner report and the replayed mutants: a -k 'a or b' selector prints bogus ids, a malformed kept list crashes the brief, a failed list write is reported as nothing written, and several checks have no test - not-stop-ship, ruled by orchestrator |
| BG1626 | Medium | drive step names lane accept as the resume of a warning stop at accept, which lane accept refuses because the verdict is already recorded - not-stop-ship, ruled by orchestrator |
| BG1627 | Medium | When lane land's bound on critic.py brief fires, critic is killed and the mutation runner its replay started is left running - not-stop-ship, ruled by orchestrator |
| BG1628 | Medium | critic.py record escapes a verdict's underscores but not its asterisks, so a ledger row reads a glob such as `name_*` or `other_*` as emphasis and markdownlint (MD037) refuses the commit - not-stop-ship, ruled by orchestrator |
| BG1629 | Medium | lane land prices a landed lane's tokens from the agent transcript but records no minutes, so every unit with a repair round reads minutes NOT MEASURED in the report - not-stop-ship, ruled by orchestrator |
| CR0746 | Medium | The session meter finds a Claude Code session's transcript store from the session id the harness exports, so a run driven from another repository is priced without SDLC_STUDIO_TRANSCRIPTS - not-stop-ship, ruled by orchestrator |
| BG1611 | Low | gate.py --red-run's regression path over-claims: a failing id that names no file files no bug, and a second red on a different test reuses the first bug without naming that test - not-stop-ship, ruled by orchestrator |
| BG1612 | Low | Two of gate.py --red-run's behaviours hold by probe but no test pins them: the sections after a bug's CI Red Runs section, and the refusal of a negative, boolean or fractional rerun limit - not-stop-ship, ruled by orchestrator |
| BG1613 | Low | ci.wait_timeout_minutes has no reader: the trunk guidance's wait fence hardcodes `timeout 30m`, so a project's override changes nothing - not-stop-ship, ruled by orchestrator |
| BG1615 | Low | mutation.py run --edits counts an edit that does not compile as killed and exits 0, and silently ignores --format and --max-mutations - not-stop-ship, ruled by orchestrator |
| BG1616 | Low | lane land's several-worktree landing moves a body line shaped like a trailer into the trailers, and three of its refusals have no test - not-stop-ship, ruled by orchestrator |
| BG1617 | Low | lane land --resume compares unit ids as raw strings, a landing stopped at rebase records no commit, and two refusals have no test - not-stop-ship, ruled by orchestrator |
| BG1618 | Low | The plan's unmetered warning gives a false reason on a re-plan, one of its test assertions cannot fail, and a fallback sentence is reached by no test - not-stop-ship, ruled by orchestrator |
| BG1619 | Low | sprint sign prints nothing when its retro write fails, so a mistyped --retro id now reaches that silence, and the close tail still prefers the scaffolded retro - not-stop-ship, ruled by orchestrator |
| BG1620 | Low | The verbatim repair brief loses the first-line indentation of a REJECT finding written over several lines, and its newest-landing choice and superseded filter have no test - not-stop-ship, ruled by orchestrator |
| BG1621 | Low | The TRD's table of committed records does not list the author mutant lists that critic.py self-check record now keeps under sdlc-studio/reviews/author-mutants/ - not-stop-ship, ruled by orchestrator |
| CR0747 | Low | critic.py record has no check mode, so a reviewer cannot confirm its verdict file will record before handing back - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M7SS62.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 7,725,828 |

Total 7,725,828, of which delegated 4,045,909. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (15 units); reviewer inherit (15 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $126.81 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 743 subagent transcript(s); total agents 21, calls 1,861, priced 46,289,662. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 353 | 10,920,236 | 23.6% | 81.6% | 8.7% | 9.6% | 173,614 | 253,889 |
| builder | 7 | 707 | 17,681,920 | 38.2% | 61.4% | 16.1% | 22.6% | 14,911 | 156,706 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 4 | 250 | 5,143,531 | 11.1% | 55.9% | 16.9% | 27.3% | 15,190 | 117,686 |
| other | 9 | 551 | 12,543,975 | 27.1% | 52.1% | 23.8% | 24.1% | 14,681 | 122,898 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44579888486/44519035594 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 8h 17m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 16 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44579888486/44519035594 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44579888486/44519035594 - no push-triggered run on main concluded failure |

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
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 4 | 48 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
