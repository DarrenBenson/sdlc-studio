# Sprint Report: RUN-01M7E52T

## Goal

A head of engineering takes a release to the change board on the run's own evidence, every cost row forecast

**Verdict: Judged achieved** - All 20 planned units (52 points) and five added in-run (6 points) delivered on independent APPROVEs, five after one repair round and US1156 after a carry answered in-run (BG1439). A release's change evidence pack is one command over committed records, naming each change's accountable person (US1155, US1156); the evidence annex documents every committed record a consumer parses, with a recomputable fingerprint and a version stamp (EP0275); the plan forecasts priced, dollar and wall-clock cost and the report states forecast, actual and ratio for every cost row (US1150, US1151); a multi-unit lane's builder is now priced per unit (BG1397). Grouping the pack by risk class is carried as CR0704, and the dollar forecast's formula, which runs high for Opus, as CR0703. BG1420 is Fixed, which clears the 6.4 tag's known-issues bar.

> **Run:** 2026-11-14T23:19:57Z to 2026-11-15T06:29:57Z (7.2h)
> **Verified on:** 38f55cf4b4ba469e36fc5dfca4dabe7725403c9b   **Fingerprint:** 41f6af509193a323

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 58 | 58 | 1.0x | 25 of 25 delivered unit(s) |
| Minutes | 326.9 | 2878.1 | 8.8x | measured active minutes (spans or agent minutes) against their forecast, over the 24 of 25 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast: the plan recorded no points per elapsed hour rate | 430.0 | no ratio | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | not forecast: the plan recorded no priced per point rate | 48,917,159 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 7,756,058 (input 4,688 x1, output 1,955,339 x5, cache write 5m 5,389,449 x1.25, cache write 1h 406,582 x2, cache read 315,858,012 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 10,802,616 | 7,756,058 | 0.72x | the whole run: forecast over 25 of 25 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 30 delegated total(s) supplied are not added |
| Priced per point | not forecast: the plan recorded no priced per point rate | 843,399 | no ratio | the Priced cost row over the 58 point(s) of the 25 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast: no priced forecast to price (the plan recorded no priced per point rate) | $131.75 | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens |
| Dollars per point | not forecast: no priced forecast to price (the plan recorded no priced per point rate) | $2.27 | no ratio | the Dollar cost row over the 58 point(s) of the 25 delivered unit(s); price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1019 | $2.48 estimated | 17.5 | 126.5 | 558,756 | 149,572 agent tokens | 876,374 priced |
| BG1268 | $1.74 estimated | 11.7 | 135.2 | 372,504 | 120,827 agent tokens | 582,183 priced |
| BG1391 | $1.32 estimated | 11.7 | 56.2 | 372,504 | 95,666 agent tokens, split by points | 427,427 priced, split by points |
| BG1393 | $1.32 estimated | 11.7 | 56.5 | 372,504 | 95,665 agent tokens, split by points | 427,427 priced, split by points |
| BG1394 | $2.69 estimated | 11.7 | 134.4 | 372,504 | 178,586 agent tokens, split by points | 935,681 priced, split by points |
| BG1397 | $2.69 estimated | 11.7 | 133.4 | 372,504 | 178,587 agent tokens, split by points | 935,681 priced, split by points |
| BG1425 | $2.44 estimated | 17.5 | 106.8 | 558,756 | 176,223 agent tokens | 761,419 priced |
| US0992 | $5.42 estimated | 29.2 | 135.4 | 931,260 | 348,834 agent tokens | 1,877,133 priced |
| US0993 | $2.40 estimated | 11.7 | 86.1 | 372,504 | 129,008 agent tokens, split by points | 880,607 priced, split by points |
| US0994 | $2.85 estimated | 17.5 | 97.9 | 558,756 | 155,858 agent tokens, split by points | 1,034,963 priced, split by points |
| US0995 | $3.69 estimated | 17.5 | 144.8 | 558,756 | 226,936 agent tokens, 1 of 2 agent totals split by points | 1,287,121 priced, 1 of 2 agent totals split by points |
| US0996 | $2.40 estimated | 11.7 | 86.8 | 372,504 | 129,007 agent tokens, split by points | 880,606 priced, split by points |
| US0999 | $1.96 estimated | 11.7 | 157.1 | 372,504 | 129,425 agent tokens | 671,737 priced |
| US1150 | $4.74 estimated | 17.5 | 223.1 | 558,756 | 466,905 agent tokens, split by points | 1,601,679 priced, split by points |
| US1151 | $4.74 estimated | 17.5 | 223.4 | 558,756 | 466,904 agent tokens, split by points | 1,601,678 priced, split by points |
| US1152 | $2.84 estimated | 17.5 | 121.7 | 558,756 | 183,900 agent tokens | 960,645 priced |
| US1153 | $1.35 estimated | 11.7 | 239.8 | 372,504 | 82,759 agent tokens, split by points | 477,810 priced, split by points |
| US1154 | $3.08 estimated | 17.5 | 257.6 | 558,756 | 211,913 agent tokens, 1 of 2 agent totals split by points | 1,044,793 priced, 1 of 2 agent totals split by points |
| US1155 | $4.38 estimated | 17.5 | 193.9 | 558,756 | 250,402 agent tokens, split by points | 1,567,807 priced, split by points |
| US1156 | $2.92 estimated | 11.7 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 166,934 agent tokens, split by points | 1,045,204 priced, split by points |
| BG1439 | $1.92 estimated | 11.7 | 57.3 | 372,504 | 136,770 agent tokens | 625,330 priced |
| BG1442 | $0.6216 estimated | 5.8 | 18.0 | 186,252 | 49,691 agent tokens, split by points | 195,837 priced, split by points |
| BG1441 | $0.6216 estimated | 5.8 | 18.9 | 186,252 | 49,690 agent tokens, split by points | 195,836 priced, split by points |
| BG1437 | $0.5593 estimated | 5.8 | 33.5 | 186,252 | 44,255 agent tokens, split by points | 183,311 priced, split by points |
| BG1445 | $0.5593 estimated | 5.8 | 33.8 | 186,252 | 44,255 agent tokens, split by points | 183,310 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 20 | 52 |
| Delivered of the plan | 20 | 52 |
| Added mid-run and delivered | 5 of 5 added | 6 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 58.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1019 | 3 | 3 | delivered | 1 |
| BG1268 | 2 | 2 | delivered | 1 |
| BG1391 | 2 | 2 | delivered | 1 |
| BG1393 | 2 | 2 | delivered | 1 |
| BG1394 | 2 | 2 | delivered | 1 |
| BG1397 | 2 | 2 | delivered | 1 |
| BG1425 | 3 | 3 | delivered | 1 |
| US0992 | 5 | 5 | delivered | 2 |
| US0993 | 2 | 2 | delivered | 1 |
| US0994 | 3 | 3 | delivered | 1 |
| US0995 | 3 | 3 | delivered | 2 |
| US0996 | 2 | 2 | delivered | 1 |
| US0999 | 2 | 2 | delivered | 1 |
| US1150 | 3 | 3 | delivered | 1 |
| US1151 | 3 | 3 | delivered | 1 |
| US1152 | 3 | 3 | delivered | 1 |
| US1153 | 2 | 2 | delivered | 1 |
| US1154 | 3 | 3 | delivered | 2 |
| US1155 | 3 | 3 | delivered | 2 |
| US1156 | 2 | 2 | delivered - discharged after it was carried at the review cap: BG1439 | 3 |
| BG1439 | 2 | 2 | added - US1156 carried at the review cap; its one blocking finding is a narrow fix in the same run's evidence pack, repaired in-run so the pack's accountable-person criterion lands with the goal (D0478); delivered | 1 |
| BG1442 | 1 | 1 | added - Main red on test_critic's one-independence-authority guard since BG1439 landed (evidence_pack.py calls critic's private _id); BG1442 fixes it and BG1441 corrects the same module's docstring in one lane, so run twelve can push green (D0480); delivered | 1 |
| BG1441 | 1 | 1 | added - Main red on test_critic's one-independence-authority guard since BG1439 landed (evidence_pack.py calls critic's private _id); BG1442 fixes it and BG1441 corrects the same module's docstring in one lane, so run twelve can push green (D0480); delivered | 1 |
| BG1437 | 1 | 1 | added - The full suite before the close is red on two push-boundary tests: the committed command audit is stale since evidence_pack.py landed (BG1437) and BG1268's class-add --phase flag stops the upgrade page's retired-flag row matching (BG1445); one lane fixes both so run twelve closes and pushes green (D0481); delivered | 1 |
| BG1445 | 1 | 1 | added - The full suite before the close is red on two push-boundary tests: the committed command audit is stale since evidence_pack.py landed (BG1437) and BG1268's class-add --phase flag stops the upgrade page's retired-flag row matching (BG1445); one lane fixes both so run twelve closes and pushes green (D0481); delivered | 1 |

## Known issues handed over

25 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0704 | High | The change evidence pack groups changes by risk and compliance class, lists high-risk changes first with their second seat's verdict, and reads through the evidence annex |
| CR0705 | High | sprint plan names the registry files a unit implies when it adds a script, a verb or reference text, before the build |
| BG1436 | Medium | A lesson class recorded with no run open retires at the next close in a clone with more than the quiet-run count of archived runs, from class-add and from retro extract alike - not-stop-ship, ruled by orchestrator |
| BG1448 | Medium | lane land spends its full hook run before a rebase conflict, and a replayed generated page merges into drift - not-stop-ship, ruled by orchestrator |
| BG1452 | Medium | reconcile derives a request Complete when every child of a partial refine resolves, though its unrefined criteria are undelivered - not-stop-ship, ruled by orchestrator |
| CR0703 | Medium | Fit the plan's dollar forecast from measured dollars per point, not priced tokens times the input price |
| BG1428 | Low | The per-unit dollars cell prices a unit's Grok agent read from a session total with no lower-bound label, and BG1391's changelog says the label holds wherever models are summed - not-stop-ship, ruled by orchestrator |
| BG1429 | Low | A project Grok price entry with a lower long-context threshold is still booked at the shipped 200,000 threshold, so a long prompt is priced at the short rate and reads exact - not-stop-ship, ruled by orchestrator |
| BG1430 | Low | verify_ac's signal relay raises its running count outside the try, so a raise in that window leaves every later returning handler refused, and no test pins the per-signal refresh of the settle bound - not-stop-ship, ruled by orchestrator |
| BG1431 | Low | Two release-notes tests take 120 s to over 300 s under load, past verify_ac's default per-verifier timeout, so BG1420's and BG1425's recorded runs fail on time unless given --timeout - not-stop-ship, ruled by orchestrator |
| BG1432 | Low | Three lane-pricing and re-close behaviours are pinned by no test: each split share's per-model split, the minutes split, and the lane-yield re-freeze over a kept window - not-stop-ship, ruled by orchestrator |
| BG1433 | Low | The report templates still say the wall-clock span has no ratio, which is wrong on a page filed under the cost-forecast mark - not-stop-ship, ruled by orchestrator |
| BG1434 | Low | The risk-class map reader drops an empty-prefix entry and a scalar risk value silently, and four refine stamping paths are pinned by no test - not-stop-ship, ruled by orchestrator |
| BG1435 | Low | retitle leaves a reference-style link definition and a link in the project-root README dangling, while its changelog says it finds every link to the renamed file - not-stop-ship, ruled by orchestrator |
| BG1438 | Low | The evidence annex says fingerprint strings escape all control characters while the reference implementation escapes only U+0000 to U+001F, and it omits the no-closed-sprint limit of the version stamp - not-stop-ship, ruled by orchestrator |
| BG1440 | Low | lane return --model with no total is dropped without a word, the model trim is untested, and help/sprint.md omits that a several-unit total is not split when a unit has no Points - not-stop-ship, ruled by orchestrator |
| BG1443 | Low | Four cost-forecast behaviours are correct but unpinned, the Minutes row's reason reads 'not forecast: not measured', and US1151's criteria name a command that never renders the rows - not-stop-ship, ruled by orchestrator |
| BG1444 | Low | sprint plan reports a malformed risk map as 'no component map is declared', says nothing when a unit's risk tag is outside the vocabulary, and no test pins which component the flag names when prefixes overlap - not-stop-ship, ruled by orchestrator |
| BG1446 | Low | Three second-seat behaviours are correct but unpinned: a story's risk tag read over its Affects, the brief's no-map default, and the first seat's latest verdict rather than its first - not-stop-ship, ruled by orchestrator |
| BG1447 | Low | tools/check_budgets.py reports every file within budget while the pre-commit budgets lane fails the same tree on docgen drift - not-stop-ship, ruled by orchestrator |
| BG1449 | Low | lane accept refuses to record a REJECT when the unit's self-check is stale, though a REJECT moves nothing - not-stop-ship, ruled by orchestrator |
| BG1450 | Low | A reviewer's verdict file is refused by critic.py record over one code span with a leading space, and the review brief does not warn - not-stop-ship, ruled by orchestrator |
| BG1451 | Low | The commit-msg hook refuses git commit --amend on a lane commit because it attributes only the newly staged files - not-stop-ship, ruled by orchestrator |
| BG1453 | Low | file_finding keeps a placeholder id such as changelog.d/BGXXXX.md in Affects verbatim instead of substituting the minted id or refusing it - not-stop-ship, ruled by orchestrator |
| BG1454 | Low | sprint lane return --agent agent-<id> leaves the unit unpriced, while lane land prints the builder as agent-<id> - not-stop-ship, ruled by orchestrator |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 3 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M7E52T.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 7,756,058 |

Total 7,756,058, of which delegated 4,268,572. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $131.01 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $0.7439 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 565 subagent transcript(s); total agents 37, calls 2,279, priced 48,917,159. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 362 | 16,712,486 | 34.2% | 88.2% | 4.9% | 6.9% | 201,197 | 408,524 |
| builder | 16 | 1,105 | 19,585,575 | 40.0% | 55.5% | 18.2% | 26.4% | 13,849 | 100,886 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 4 | 135 | 1,676,022 | 3.4% | 47.2% | 21.1% | 31.7% | 14,011 | 60,718 |
| other | 16 | 677 | 10,943,076 | 22.4% | 47.4% | 25.8% | 26.8% | 14,516 | 79,907 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 36 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 36 commit(s) on main inside the run window |
| Lead time for changes | 6h 32m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 36 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

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

7 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 5 | 0 | 5 | delete candidate: 10 refusal(s) over 3 runs and no candidate catch |
| markdown | 2 | 0 | 2 | delete candidate: 10 refusal(s) over 3 runs and no candidate catch |

### Lessons

4 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 3 | 33 |
| LC-019 | a push-gate guard the per-commit run skips | active | 0 | 0 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 0 |
