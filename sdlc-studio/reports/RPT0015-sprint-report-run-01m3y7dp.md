# Sprint Report: RUN-01M3Y7DP

## Goal

Maya signs a sprint report whose delivery, cost and DORA figures match what the run actually did

**Verdict: Judged achieved** - 8 of 8 units approved by an independent QA seat (BG0895 discharged by its rejecting reviewer after a carry), every batch unit verifies green. This run's own page measures what RPT0014 could not: every unit carries an agent total from its lane return (builder) and the run carries the reviewers' spend, so tokens read 2.17M against a 1.28M forecast (1.69x), 1.53M of it the builders and reviewers, where RPT0014 printed 0.2x; a discharged carry counts as delivered (BG0890); time to restore pairs by creation and reads no restore needed for a run with no red (BG0891); the header names its window end (BG0893); a close gap holds only failures (BG0894); a batch finding no longer moves a signed page and the checklist agrees with the page on a re-close (BG0895); velocity rows keep their model (BG0892). Disclosed, out of scope at the goal review: the minutes ratio compares wall-clock with active work (BG0898) and the minutes rate still falls back to a July row (BG0907).

> **Run:** 2026-10-02T11:48:33Z to 2026-10-02T16:44:56Z (4.9h)
> **Verified on:** e04cf69d658e5a2088ad357e5a761d8ffdbc644b   **Fingerprint:** b876e218da58edf6

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 16 | 16 | 1.0x | 8 of 8 delivered unit(s) |
| Minutes | 102.4 | 296.4 | 2.89x | the whole run: forecast over 8 of 8 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 1,283,008 | 4,920,336 | 3.84x | the whole run: forecast over 8 of 8 unit(s) planned or added and not dropped; actual is the main-thread meter plus 16 delegated agent(s)' reported totals, split in the appendix |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. Spans of
units open at the same time overlap, so no per-unit figure is added up into the run's figures
above.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0890 | 19.2 | 13.0 agent minutes | 240,564 | 52,891 agent tokens |
| BG0891 | 6.4 | 18.0 agent minutes | 80,188 | 60,623 agent tokens |
| BG0892 | 12.8 | 10.0 agent minutes | 160,376 | 40,792 agent tokens |
| BG0895 | 12.8 | 45.0 agent minutes | 160,376 | 75,828 agent tokens |
| US0979 | 19.2 | 37.0 agent minutes | 240,564 | 304,928 agent tokens |
| US0980 | 19.2 | 28.0 agent minutes | 240,564 | 114,676 agent tokens |
| BG0893 | 6.4 | 9.0 agent minutes | 80,188 | 24,294 agent tokens |
| BG0894 | 6.4 | 9.0 agent minutes | 80,188 | 18,210 agent tokens |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 8 | 16 |
| Delivered of the plan | 8 | 16 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 16.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0890 | 3 | 3 | delivered | 2 |
| BG0891 | 1 | 1 | delivered | 2 |
| BG0892 | 2 | 2 | delivered | 2 |
| BG0895 | 2 | 2 | delivered - discharged after it was carried at the review cap: BG0909 | 3 |
| US0979 | 3 | 3 | delivered | 1 |
| US0980 | 3 | 3 | delivered | 2 |
| BG0893 | 1 | 1 | delivered | 1 |
| BG0894 | 1 | 1 | delivered | 1 |

## Known issues handed over

12 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0608 | Medium | Prevent or retire lesson LC-005 (repair breaks its neighbour) |
| BG0899 | Low | A lane brief reopens the span of a unit already at a terminal status - not-stop-ship, ruled by Claude (orchestrator) |
| BG0900 | Low | The report drops the delegated token total from the run's actual when the session meter reads zero - not-stop-ship, ruled by Claude (orchestrator) |
| BG0901 | Low | Two agent totals on one unit, one without minutes, fall back to the span unlabelled - not-stop-ship, ruled by Claude (orchestrator) |
| BG0902 | Low | A late lane return --tokens writes into a sealed run and invalidates its signed page - not-stop-ship, ruled by Claude (orchestrator) |
| BG0903 | Low | lane return and lane brief take agent totals silently in three cases - not-stop-ship, ruled by Claude (orchestrator) |
| BG0904 | Low | DORA counts a cancelled or skipped CI run on main as a failed deployment - not-stop-ship, ruled by Claude (orchestrator) |
| BG0905 | Low | The tokens-ratio withheld rule's delivered-unit half is untested, and its help text says briefed where the code counts any span - not-stop-ship, ruled by Claude (orchestrator) |
| BG0906 | Low | Two of D0304's time-to-restore rules are unpinned: the FIRST success restores, and an in-progress run ends no streak - not-stop-ship, ruled by Claude (orchestrator) |
| BG0907 | Low | Calibration's minutes per point falls back to a July row because velocity rows carry no wall time - not-stop-ship, ruled by Claude (orchestrator) |
| BG0908 | Low | Close steps hand over their status and prose lines as known issues - not-stop-ship, ruled by Claude (orchestrator) |
| BG0910 | Low | The close pre-flight's live checklist read is unpinned - not-stop-ship, ruled by Claude (orchestrator) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3Y7DP.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 3,392,159 |

Total 4,920,336, of which delegated 1,528,177. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 37025767700/37020451101/37016645468/37003594324 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 4h 49m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 36 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | forge runs 37025767700/37020451101/37016645468/37003594324 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 37025767700/37020451101/37016645468/37003594324 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 80,188 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 8 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |
| stamps-staged | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| style | 1 | 1 | 0 | 2 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | 4 candidate catch(es) over 3 runs |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-005 | repair breaks its neighbour | graduating (CR0608) | 1 | 3 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-013 | suite verdict before the commit | active | 0 | 0 |
| LC-014 | paperwork during a build | active | 1 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | active | 0 | 0 |
