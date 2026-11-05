# Sprint Report: RUN-01M6NH7W

## Goal

A sprint costs at most 1.5M priced tokens per point, each lane priced from its builder's own transcript

**Verdict: Judged achieved** - 36.3M priced for 29 delivered points before the close, about 1.25M a point against the 1.5M goal and run five's 2.54M; every delegated lane is priced from its builder's transcript

> **Run:** 2026-11-05T09:43:16Z to 2026-11-05T18:20:40Z (8.6h)
> **Verified on:** 8c7db8dee71c0e9c9f3bdca20e2d4945ccfdca71   **Fingerprint:** 695c0b4a97bb1ccf

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 27 | 27 | 1.0x | 12 of 13 delivered unit(s) |
| Minutes | 157.6 | 269.0 | 1.71x | measured active minutes (spans or agent minutes) against their forecast, over the 12 of 13 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 517.4 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 36,820,993 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 5,883,977 (input 3,636 x1, output 988,495 x5, cache write 5m 4,490,874 x1.25, cache write 1h 400,972 x2, cache read 254,593,459 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 5,028,804 | 5,883,977 | 1.17x | the whole run: forecast over 12 of 13 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 17 delegated total(s) supplied are not added |
| Priced per point | not forecast | 1,269,689 | no ratio | the Priced cost row over the 29 point(s) of the 13 delivered unit(s), in priced input-equivalent tokens per point |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- |
| US1117 | 17.5 | 42.0 agent minutes | 558,756 | 333,035 agent tokens | 1,731,554 priced |
| US1118 | 29.2 | 23.0 agent minutes | 931,260 | 211,319 agent tokens | 1,360,603 priced |
| US1120 | 11.7 | 19.0 agent minutes | 372,504 | 139,364 agent tokens | 601,798 priced |
| US1119 | 11.7 | 19.0 agent minutes | 372,504 | 194,520 agent tokens | 1,078,646 priced |
| BG1224 | 17.5 | 20.0 agent minutes | 558,756 | 139,963 agent tokens | 816,826 priced |
| BG1223 | 5.8 | 11.0 agent minutes | 186,252 | 118,083 agent tokens | 518,946 priced |
| BG1213 | 5.8 | 9.0 agent minutes | 186,252 | 120,366 agent tokens | 514,178 priced |
| US1121 | 17.5 | 35.0 agent minutes | 558,756 | 379,986 agent tokens | 1,605,060 priced |
| BG1220 | 11.7 | 19.0 agent minutes | 372,504 | 156,693 agent tokens | 783,023 priced |
| BG1217 | 11.7 | 22.0 agent minutes | 372,504 | 147,501 agent tokens | 596,941 priced |
| BG1226 | 11.7 | 33.0 agent minutes | 372,504 | 539,112 agent tokens | 1,938,434 priced |
| BG1227 | 5.8 | 17.0 agent minutes | 186,252 | 140,945 agent tokens | 544,106 priced |
| BG1236 | NOT MEASURED - not in the plan | 10.0 agent minutes | NOT MEASURED - not in the plan | 133,290 agent tokens | 787,928 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 11 | 26 |
| Delivered of the plan | 10 | 24 |
| Added mid-run and delivered | 3 of 3 added | NOT MEASURED - not in the plan snapshot: BG1236 |
| Dropped | 1 | 2 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 29.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1117 | 3 | 3 | delivered | 2 |
| US1118 | 5 | 5 | delivered | 1 |
| US1120 | 2 | 2 | delivered | 2 |
| US1119 | 2 | 2 | delivered | 2 |
| BG1224 | 3 | 3 | delivered | 2 |
| BG1223 | 1 | 1 | delivered | 1 |
| BG1213 | 1 | 1 | delivered | 1 |
| US1121 | 3 | 3 | delivered | 2 |
| BG1220 | 2 | 2 | delivered | 1 |
| BG1190 | 2 | 2 | dropped - carried at the review cap: BG1228 | 2 |
| BG1217 | 2 | 2 | delivered | 1 |
| BG1226 | 2 | 2 | added - D0408: an efficiency fix found in run six's own landings; delivered | 2 |
| BG1227 | 1 | 1 | added - D0408: an efficiency fix found in run six's own landings; delivered | 1 |
| BG1236 | NOT MEASURED - not in the plan snapshot | 2 | added - D0404: the push gate's full suite found five census tests red after run six's landings; delivered | 2 |

## Known issues handed over

12 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0663 | High | Run the commit-time suites on the gate host, as the push already does - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1228 | Medium | BG1190 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1229 | Medium | critic.py's self-check and verdict records refuse shapes authors and reviewers write naturally, and record has no dry run - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| CR0664 | Medium | Prevent or retire lesson LC-017 (a page-format rule mark nothing round-trips) |
| BG1225 | Low | An http loopback Cursor API base still goes through an http_proxy in cleartext with the key on it - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1230 | Low | lane return --agent: one agent priced onto two units, stale --tokens wording, and undocumented help - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1231 | Low | lane land: exit 1 documented too narrowly, two test gaps, a false --units help line, and an unscrubbed git environment - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1232 | Low | The lane brief's budget and hand-in: no-Points untested, one shared hand-in for a multi-unit lane, and US1093's stale story text - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1233 | Low | The Cursor hook ledger: mid-run creation or deletion misreads the run, deep nesting is fatal, and the text cut is untested - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1234 | Low | Small follow-ups from run six's approved bug fixes: BG1217, BG1220, BG1223, BG1224 and BG1227 - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1235 | Low | Run six's round-2 and lane accept follow-ups: an unfailing help pin, unpinned counts, and accept's late refusals - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1237 | Low | Orchestration frictions: batch add takes an id with no file, and a re-review's prior-finding notes parse as a blocking item - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 1 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M6NH7W.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 5,883,977 |

Total 5,883,977, of which delegated 3,018,172. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 21 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 21 commit(s) on main inside the run window |
| Lead time for changes | 7h 10m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 21 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

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

6 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 6 refusal(s) over 3 runs and no candidate catch |
| markdown | 3 | 0 | 3 | delete candidate: 7 refusal(s) over 3 runs and no candidate catch |
| message-refs | 2 | 0 | 2 | delete candidate: 7 refusal(s) over 3 runs and no candidate catch |
| style | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

3 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | active | 0 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 1 | 2 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 3 | 27 |
