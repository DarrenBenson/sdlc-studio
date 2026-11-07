# Sprint Report: RUN-01M6RZQZ

## Goal

Run seven's cost features hold in every harness, and every consuming agent starts and commits leaner

**Verdict: Judged partial** - Run seven's cost features now hold: all seven hardening bugs are Fixed and the non-Claude models are priced (US1135), and every agent starts leaner (AGENTS.md at 6,580 chars, the lean builder and reviewer definitions at about 16k start context against 34k). Commits got only partly leaner: the self-written trailers landed after a carry (US1133, fixed in-run as BG1274), the quiet commit path (US1134) went to 6.4 under D0419, and Copilot's token billing (CR0685) and the pricing gaps (BG1266) are carried.

> **Run:** 2026-11-06T17:42:55Z to 2026-11-06T22:32:18Z (4.8h)
> **Verified on:** 06eac03d7abcf2fea129fa925bae2e78746aa0eb   **Fingerprint:** 17a047f494e68304

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 41 | 41 | 1.0x | 17 of 17 delivered unit(s) |
| Minutes | 181.0 | 819.4 | 4.53x | measured active minutes (spans or agent minutes) against their forecast, over the 11 of 17 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 289.4 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 44,550,286 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 6,209,549 (input 3,590 x1, output 1,754,886 x5, cache write 5m 4,055,443 x1.25, cache write 1h 395,630 x2, cache read 299,117,027 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 7,636,332 | 6,209,549 | 0.81x | the whole run: forecast over 17 of 17 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 15 delegated total(s) supplied are not added |
| Priced per point | not forecast | 1,086,592 | no ratio | the Priced cost row over the 41 point(s) of the 17 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast | $118.38 | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-06; covers 100.0% of the priced tokens |
| Dollars per point | not forecast | $2.89 | no ratio | the Dollar cost row over the 41 point(s) of the 17 delivered unit(s); price table effective 2026-11-06 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1240 | $1.68 estimated | 11.7 | 51.7 | 372,504 | 137,124 agent tokens | 533,229 priced |
| BG1244 | $2.53 estimated | 11.7 | 52.1 | 372,504 | 179,976 agent tokens | 832,585 priced |
| BG1245 | $4.58 estimated | 29.2 | 90.2 | 931,260 | 267,679 agent tokens | 1,636,099 priced |
| BG1246 | $2.04 estimated | 11.7 | 52.5 | 372,504 | 163,156 agent tokens | 636,069 priced |
| BG1242 | $3.81 estimated | 17.5 | 94.0 | 558,756 | 232,579 agent tokens | 1,352,428 priced |
| US1129 | $3.29 estimated | 17.5 | 155.1 | 558,756 | 208,828 agent tokens | 1,148,224 priced |
| US1131 | $2.25 estimated | 17.5 | 40.1 | 558,756 | 164,292 agent tokens | 751,797 priced |
| BG1252 | $2.08 estimated | 11.7 | 65.6 | 372,504 | 149,838 agent tokens | 682,948 priced |
| BG1254 | $3.41 estimated | 17.5 | 66.3 | 558,756 | 215,644 agent tokens | 1,150,923 priced |
| US1132 | $5.11 estimated | 17.5 | 90.7 | 558,756 | 367,272 agent tokens | 1,686,209 priced |
| US1135 | $3.37 estimated | 17.5 | 60.9 | 558,756 | 224,783 agent tokens | 1,123,518 priced |
| BG1257 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1257 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1257 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1257 --agent A` |
| BG1258 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1258 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1258 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1258 --agent A` |
| BG1259 | $0.4584 estimated | 5.8 | NOT MEASURED - 0 of its 1 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 186,252 | 43,940 agent tokens | 133,295 priced |
| BG1273 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1273 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1273 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1273 --agent A` |
| BG1274 | $1.84 estimated | 17.5 | NOT MEASURED - 0 of its 1 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 558,756 | 133,991 agent tokens | 585,300 priced |
| BG1278 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1278 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1278 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1278 --agent A` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 14 | 40 |
| Delivered of the plan | 11 | 31 |
| Added mid-run and delivered | 6 of 6 added | 10 |
| Dropped | 3 | 9 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 41.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1240 | 2 | 2 | delivered | 1 |
| BG1244 | 2 | 2 | delivered | 1 |
| BG1245 | 5 | 5 | delivered | 1 |
| BG1246 | 2 | 2 | delivered | 1 |
| BG1242 | 3 | 3 | delivered | 1 |
| US1129 | 3 | 3 | delivered | 2 |
| US1130 | 3 | 3 | dropped - carried at the review cap: BG1258 | 2 |
| US1131 | 3 | 3 | delivered | 1 |
| BG1252 | 2 | 2 | delivered | 1 |
| BG1254 | 3 | 3 | delivered | 1 |
| US1132 | 3 | 3 | delivered | 2 |
| US1133 | 3 | 3 | dropped - carried at the review cap: BG1274 | 2 |
| US1135 | 3 | 3 | delivered | 1 |
| US1134 | 3 | 3 | dropped - D0419: two of three criteria unstarted and eight tests outside its Affects turn red; to 6.4 | 0 |
| BG1257 | 1 | 1 | added - D0418: the wall-clock census refused BG1246's unmarked bounded test; delivered | 1 |
| BG1258 | 3 | 3 | added - D0419: carries US1130 at the cap; two false sentences, one in the 6.3 release notes; delivered | 1 |
| BG1259 | 1 | 1 | added - D0420: the forge Lint job is red on a bandit false positive; delivered | 2 |
| BG1273 | 1 | 1 | added - D0421: the push gate's confinement sweep refused engagement_floor.py; delivered | 1 |
| BG1274 | 3 | 3 | added - D0422: carries US1133; the live hook still refuses correct Refs on two declaration shapes; delivered | 2 |
| BG1278 | 1 | 1 | added - D0426: the push gate's rename guard refused BG1274's fixture; delivered | 1 |

## Known issues handed over

18 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1260 | Medium | `init run` and `init guided` exit 1 and leave a half-built project when `.claude` is a regular file, which the base initialised cleanly - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1261 | Medium | After BG1245 a hard kill of `sprint.py`'s process group no longer reaches a running lane, whose CLI runs on in the worktree with no timeout over it - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1262 | Medium | `sprint lane run` kills a timed-out lane with no `SIGTERM` first, leaving `index.lock` behind, and leaves four further lane rules unhandled or unpinned - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1264 | Medium | US1133's trailer check skips a single-id subject though its docs say it does not, refuses this repository's paperwork-commit convention, and leaves two ownership rules unpinned - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1265 | Medium | Reviewers' throwaway copies of the repository are never removed and carry no history, so they fill the temp quota and fail history-dependent tests each reviewer must then triage - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1268 | Medium | No shipped command writes a row to `sdlc-studio/lessons.jsonl`, the store the lane brief reads, and its build digest is full at five, so the next build lesson drops one US1132's AC3 needs - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1272 | Medium | The pre-push check reads only the latest Lint run, so a push made while the previous run is still in progress never sees it fail - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| CR0685 | Medium | Price a GitHub Copilot run per token in AI credits, the billing Copilot moved to on 2026-06-01, and keep the premium-request price only for plans still billed by request - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1263 | Low | The commit-msg hook reads `Refs:` lines below git's scissors line, so a `git commit -v` whose diff shows such a line is refused as a contradicted trailer - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1266 | Low | The dollar report and price table leave the run's end date, a signed table edit, the premium-request override and four price slots unpinned, and word an unsigned table edit as a tree change - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1267 | Low | `sprint.py lane return` prints a two-model session's `lane run cost` at the largest model's rate, and BG1244's fragment misstates what the parser did before - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1269 | Low | `sprint plan` puts every unit in one shared-file cluster when they share a reference doc, so a collision in one code file is hidden and nothing keeps those units sequential - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1270 | Low | The always-loaded instruction cuts leave their restored rules and their budget gate unpinned, and a keep-indicator description escapes the 600-char cap - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1271 | Low | `sprint cost --anatomy` counts a call from the second the run opened that the opening reading already holds, reads a zero, negative or quoted start budget as none, and leaves three boundaries and an AC2 pin loose - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |
| BG1275 | Low | Two statements from run eight's last repairs claim more than the code or its tests show - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0424) |
| BG1276 | Low | The footprint counter splits Affects on every comma, so a path inside a bracketed note is dropped from the unit's file count - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0424) |
| BG1277 | Low | The close's closing-review row does not credit a unit carried at the review cap whose carrying bug was fixed and approved in the same run - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0425) |
| CR0686 | Low | Carry the hand-back contract in a project's own seat cards and in `amigo-template.md`, not only in the shipped default seats - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0423) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-07T00:15:19Z | 17a047f494e68304 |

Signing records the principal, the date and this report's fingerprint against RUN-01M6RZQZ.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 6,209,549 |

Total 6,209,549, of which delegated 2,489,102. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 368 subagent transcript(s); total agents 42, calls 1,729, priced 44,550,286. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 248 | 20,027,367 | 45.0% | 92.2% | 4.0% | 3.9% | 699,405 | 745,930 |
| builder | 13 | 664 | 11,595,235 | 26.0% | 51.9% | 17.2% | 30.9% | 25,730 | 92,975 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 2 | 52 | 657,390 | 1.5% | 40.4% | 23.7% | 35.9% | 16,621 | 53,493 |
| other | 26 | 765 | 12,270,295 | 27.5% | 42.2% | 23.7% | 34.1% | 17,123 | 70,672 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 19 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 19 commit(s) on main inside the run window |
| Lead time for changes | 5h 15m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 19 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 1 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

1 gate(s) were not holding when this page was derived

- **D0425** - rule:sprint-checklist:closing-review (2026-11-06T22:00:09+00:00): RUN-01M6RZQZ: the row reads each unit's latest verdict, and US1130 and US1133 end on correct round-2 REJECTs because each was carried at the review cap. Their findings were carried as BG1258 and BG1274, both in this batch and both Fixed on independent APPROVEs (BG1258 round 1; BG1274 round 2), so the defects the REJECTs found are fixed and independently reviewed. The row does not read a carry discharged through its carrying bug, filed as a bug at this close. Precedent: D0131. [kind: deliberate] [authorised by: Claude Opus 5.5 (orchestrator, under the operator's standing rule that sprints run autonomously; named for the operator at the sign)]

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 5 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | graduating (CR0684) | 1 | 3 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 0 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 1 | 30 |
| LC-019 | a push-gate guard the per-commit run skips | active | 0 | 0 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 0 |
