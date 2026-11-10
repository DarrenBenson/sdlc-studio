# Sprint Report: RUN-01M7061X

## Goal

Abena Osei becomes Primary, Copilot, Grok and Composer runs are priced, and waves resume from a short brief

**Verdict: Judged achieved** - Abena Osei is the shipped skill's Primary (US1146), Grok, Composer and Copilot runs are priced (US1143-US1145), and sprint handoff and resume work from a brief of at most 8k tokens (US1140-US1142, BG1312); US1147 was carried and US1134 and BG1300 descoped, none of them a clause of the goal

> **Run:** 2026-11-09T13:11:17Z to 2026-11-09T19:37:34Z (6.4h)
> **Verified on:** 4574915d6ad735113209451a13573c62eedcfa8d   **Fingerprint:** 15154fd97f127085

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 51 | 51 | 1.0x | 19 of 19 delivered unit(s) |
| Minutes | 297.7 | 1248.6 | 4.19x | measured active minutes (spans or agent minutes) against their forecast, over the 19 of 19 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 386.3 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 46,104,977 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 7,034,693 (input 4,114 x1, output 2,074,532 x5, cache write 5m 4,096,258 x1.25, cache write 1h 859,789 x2, cache read 288,883,021 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 9,498,852 | 7,034,693 | 0.74x | the whole run: forecast over 19 of 19 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 5 delegated total(s) supplied are not added |
| Priced per point | not forecast | 904,019 | no ratio | the Priced cost row over the 51 point(s) of the 19 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast | $126.64 | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-09; covers 100.0% of the priced tokens |
| Dollars per point | not forecast | $2.48 | no ratio | the Dollar cost row over the 51 point(s) of the 19 delivered unit(s); price table effective 2026-11-09 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1205 | NOT MEASURED - no agent returned for it was priced from its own transcript | 29.2 | 47.0 | 931,260 | 2,005,255 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1205 --agent A` |
| BG1264 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 60.1 | 372,504 | 1,844,227 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1264 --agent A` |
| US0986 | $4.16 estimated | 29.2 | 47.2 | 931,260 | 234,759 agent tokens | 1,511,769 priced |
| US1130 | $2.31 estimated | 17.5 | 147.0 | 558,756 | 149,319 agent tokens | 782,313 priced |
| US1133 | $3.74 estimated | 17.5 | 59.0 | 558,756 | 241,700 agent tokens | 1,249,586 priced |
| US1140 | NOT MEASURED - no agent returned for it was priced from its own transcript | 29.2 | 45.0 | 931,260 | 1,924,112 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1140 --agent A` |
| US1141 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 147.7 | 558,756 | 2,206,332 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1141 --agent A` |
| US1142 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 29.1 | 372,504 | 332,327 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1142 --agent A` |
| US1143 | $4.12 estimated | 11.7 | 59.5 | 372,504 | 305,671 agent tokens | 1,293,191 priced |
| US1144 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 136.6 | 558,756 | 1,699,494 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1144 --agent A` |
| US1145 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 81.9 | 372,504 | 1,846,707 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1145 --agent A` |
| US1146 | NOT MEASURED - no agent returned for it was priced from its own transcript | 29.2 | 73.4 | 931,260 | 2,929,618 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1146 --agent A` |
| US1148 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 40.7 | 558,756 | 1,106,864 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units US1148 --agent A` |
| BG1302 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 73.2 | 186,252 | 2,930,959 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1302 --agent A` |
| BG1303 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 73.5 | 186,252 | 2,935,561 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1303 --agent A` |
| BG1312 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 42.5 | 372,504 | 1,509,452 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1312 --agent A` |
| BG1318 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 32.1 | 186,252 | 1,014,166 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1318 --agent A` |
| BG1320 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 31.3 | 186,252 | 548,265 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1320 --agent A` |
| BG1329 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 21.9 | 372,504 | 183,931 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1329 --agent A` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 18 | 53 |
| Delivered of the plan | 15 | 45 |
| Added mid-run and delivered | 4 of 4 added | 6 |
| Dropped | 3 | 8 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 51.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1205 | 5 | 5 | delivered | 1 |
| BG1264 | 2 | 2 | delivered | 1 |
| BG1300 | 2 | 2 | dropped - D0454: its tests must run with a temporary HOME, which the worktree guard refuses; run ten builds it once the operator's rule is in place | 0 |
| US0986 | 5 | 5 | delivered | 1 |
| US1130 | 3 | 3 | delivered | 1 |
| US1133 | 3 | 3 | delivered | 1 |
| US1134 | 3 | 3 | dropped - D0453: the change reaches 8 test modules beyond its Affects; re-groom before rebuilding | 0 |
| US1140 | 5 | 5 | delivered | 1 |
| US1141 | 3 | 3 | delivered | 1 |
| US1142 | 2 | 2 | delivered | 1 |
| US1143 | 2 | 2 | delivered | 2 |
| US1144 | 3 | 3 | delivered | 1 |
| US1145 | 2 | 2 | delivered | 1 |
| US1146 | 5 | 5 | delivered | 1 |
| US1147 | 3 | 3 | dropped - carried at the review cap: BG1318 | 2 |
| US1148 | 3 | 3 | delivered | 1 |
| BG1302 | 1 | 1 | delivered | 1 |
| BG1303 | 1 | 1 | delivered | 1 |
| BG1312 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1318 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1320 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1329 | 2 | 2 | added - no reason recorded; delivered | 1 |

## Known issues handed over

17 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1310 | Medium | `tools/skill-tests.sh`, the unittest runner `npm test` uses, loads no conftest, so the harness-variable scrub BG1197 added never runs there and the meter tests fail under a Cursor session - not-stop-ship, ruled by orchestrator |
| BG1309 | Low | A Cursor Composer or Grok session in Fast mode is priced at the standard rate, because the model id a reading carries cannot tell Fast from standard - not-stop-ship, ruled by orchestrator |
| BG1311 | Low | `sprint.py lane land` removes the builder's worktree, so the builder cannot be resumed for a repair after a REJECT and a fresh builder must re-read the unit from cold - not-stop-ship, ruled by orchestrator |
| BG1313 | Low | The resume brief has three edges its tests do not pin: a batch listed out of plan order, a `-qa.none` landing marker read as in flight, and a Sprint Goal holding a newline that breaks `parse` - not-stop-ship, ruled by orchestrator |
| BG1314 | Low | Two US1146 persona checks cannot catch a swapped Primary, and `validate.py personas` compares the whole Interface cell, so a card reverted to Primary passes AC2's own Verify - not-stop-ship, ruled by orchestrator |
| BG1315 | Low | `help/sprint.md` still names a lane hand-in `<unit>-claims.json` under the id as typed, which BG1303's landing now keys by the normalised id, and `refine seams` still pairs a schema-3 unit with itself - not-stop-ship, ruled by orchestrator |
| BG1316 | Low | `sprint.py handoff` silently drops an `--agent` naming a unit outside the batch, both new verbs crash on an unreadable run state, and the next-step line's stream is unpinned - not-stop-ship, ruled by orchestrator |
| BG1317 | Low | A Copilot `credit_usd` of 0 is accepted and prices every Copilot reading at $0, and reference-sprint.md's list of price sources omits the newer ones - not-stop-ship, ruled by orchestrator |
| BG1319 | Low | Five Copilot model ids priced from the shared OpenAI entries stay token-priced under `pricing.copilot_billing: requests`, so a request-billed Copilot run on one of them is billed twice - not-stop-ship, ruled by orchestrator |
| BG1321 | Low | Trevor Hale's Scenario check misses a capitalised offer and a negation outside its word list, so changelog.d/US1147.md claims more than the AC7 test holds - not-stop-ship, ruled by orchestrator |
| BG1322 | Low | The commit-msg trailer check still refuses commit 089008d5's `Refs: US1090`, whose only record is a waiver row in decisions.md - not-stop-ship, ruled by orchestrator |
| BG1323 | Low | The commit-msg hook misses git's scissors line under a non-default `core.commentChar`, the multi-id rule still reads trailers below it, and `_ledger_rows` and BG1264's fragment say an edited ledger row owns nothing - not-stop-ship, ruled by orchestrator |
| BG1324 | Low | No test replays a page filed before the Copilot billing basis existed, a mixed run's page drops the 'plan bills by request' reason, and US1145's lane-return test copies the call instead of running it - not-stop-ship, ruled by orchestrator |
| BG1325 | Low | A hand-run mutation pass can leave a stale `.pyc` that Python reuses after the source is restored, so a later test run, the commit hook's among them, judges the mutant rather than the code - not-stop-ship, ruled by orchestrator |
| BG1326 | Low | `sprint.py handoff` writes a resume brief while a lane is still in flight, so the wave boundary reference-sprint.md defines is stated but not enforced, and four files still say no command writes a handoff - not-stop-ship, ruled by orchestrator |
| BG1327 | Low | A verdict file's `\;` escape, which the review brief prescribes for a semicolon inside a finding, still splits the finding when `critic.py record --from-verdict` reads it, leaving an untagged piece the record refuses - not-stop-ship, ruled by orchestrator |
| BG1328 | Low | `artifact.py new --type story --epic <a Done epic>` leaves the epic Done, so its parent request derives Complete although the new story is Draft, and `refine apply` refuses to add the deferred slice of an already-decomposed request - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-10T12:16:45Z | 15154fd97f127085 |

Signing records the principal, the date and this report's fingerprint against RUN-01M7061X.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 7,034,693 |

Total 7,034,693, of which delegated 931,449. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 444 subagent transcript(s); total agents 39, calls 1,997, priced 46,104,977. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 294 | 18,033,441 | 39.1% | 84.5% | 9.5% | 6.0% | 313,815 | 521,234 |
| builder | 4 | 261 | 4,352,766 | 9.4% | 53.4% | 15.5% | 31.1% | 13,275 | 91,047 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 1 | 34 | 484,093 | 1.0% | 38.1% | 20.7% | 41.2% | 13,606 | 56,633 |
| other | 33 | 1,408 | 23,234,676 | 50.4% | 48.0% | 18.7% | 33.3% | 13,341 | 81,613 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 42676771245/42631225553 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 7h 2m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 29 commit(s) |
| Change failure rate | 50% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 42676771245/42631225553 - 2 deployment(s); 1 failed on d56502a785bb6f32c878a3c8f1fef213827aa970 |
| Time to restore | not restored | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 42676771245 - main went red at run 42676771245, and no push-triggered run created after it concluded success in the run window |

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

3 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 3 | 0 | 3 | delete candidate: 5 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | graduating (CR0684) | 0 | 3 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 0 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 0 | 30 |
| LC-019 | a push-gate guard the per-commit run skips | active | 0 | 0 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 0 |
