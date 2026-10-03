# Sprint Report: RUN-01M3ZAGE

## Goal

Maya signs a sprint report whose every figure is true, and every tool reports only what it judged.

**Verdict: Judged achieved** - Every unit in the batch was delivered and approved by an independent reviewer, including two carries discharged by the reviewer who rejected them; the report's figures each derive from what the close froze.

> **Run:** 2026-10-02T22:06:20Z to 2026-10-03T04:10:27Z (6.1h)
> **Verified on:** ba7787e70c56f03bef1ac132db92738246c4a244   **Fingerprint:** 24f98f9dc36eb7f6

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 53 | 53 | 1.0x | 37 of 37 delivered unit(s) |
| Minutes | 339.2 | 309.5 | 0.91x | measured active minutes (spans or agent minutes) against their forecast, over the 37 of 37 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 364.1 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Tokens | 3,555,876 | 7,753,004 | 2.18x | the whole run: forecast over 37 of 37 unit(s) planned or added and not dropped; actual is the main-thread meter plus 53 delegated agent(s)' reported totals, split in the appendix |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0911 | 12.8 | 9.0 agent minutes | 134,184 | 61,306 agent tokens |
| BG0912 | 12.8 | 12.9 agent minutes | 134,184 | 85,125 agent tokens |
| BG0913 | 12.8 | 19.6 agent minutes | 134,184 | 134,805 agent tokens |
| BG0898 | 12.8 | 29.7 agent minutes | 134,184 | 182,138 agent tokens |
| BG0899 | 6.4 | 4.4 agent minutes | 67,092 | 31,449 agent tokens |
| BG0900 | 6.4 | 8.7 agent minutes | 67,092 | 61,693 agent tokens |
| BG0901 | 6.4 | 10.2 agent minutes | 67,092 | 63,714 agent tokens |
| BG0903 | 6.4 | 7.2 agent minutes | 67,092 | 47,652 agent tokens |
| BG0904 | 6.4 | 4.7 agent minutes | 67,092 | 29,454 agent tokens |
| BG0908 | 12.8 | 4.8 agent minutes | 134,184 | 34,233 agent tokens |
| BG0907 | 12.8 | 12.6 agent minutes | 134,184 | 93,933 agent tokens |
| BG0914 | 6.4 | 5.9 agent minutes | 67,092 | 39,685 agent tokens |
| BG0905 | 6.4 | 4.7 agent minutes | 67,092 | 29,454 agent tokens |
| BG0906 | 6.4 | 1.6 agent minutes | 67,092 | 9818 agent tokens |
| BG0910 | 6.4 | 1.6 agent minutes | 67,092 | 9818 agent tokens |
| US0982 | 6.4 | 3.3 agent minutes | 67,092 | 23,259 agent tokens |
| BG0870 | 12.8 | 3.1 agent minutes | 134,184 | 27,719 agent tokens |
| BG0871 | 12.8 | 11.0 agent minutes | 134,184 | 97,015 agent tokens |
| BG0872 | 12.8 | 2.4 agent minutes | 134,184 | 16,564 agent tokens |
| BG0873 | 12.8 | 3.6 agent minutes | 134,184 | 24,846 agent tokens |
| BG0878 | 19.2 | 17.0 agent minutes | 201,276 | 133,903 agent tokens |
| BG0882 | 12.8 | 4.8 agent minutes | 134,184 | 33,128 agent tokens |
| BG0902 | 6.4 | 4.8 agent minutes | 67,092 | 33,128 agent tokens |
| BG0885 | 12.8 | 51.3 agent minutes | 134,184 | 304,180 agent tokens |
| US0981 | 6.4 | 3.6 agent minutes | 67,092 | 24,846 agent tokens |
| BG0886 | 6.4 | 2.4 agent minutes | 67,092 | 16,563 agent tokens |
| BG0887 | 6.4 | 3.1 agent minutes | 67,092 | 27,719 agent tokens |
| BG0888 | 6.4 | 2.4 agent minutes | 67,092 | 20,789 agent tokens |
| BG0889 | 12.8 | 7.9 agent minutes | 134,184 | 69,296 agent tokens |
| BG0896 | 6.4 | 4.7 agent minutes | 67,092 | 41,578 agent tokens |
| BG0915 | 12.8 | 6.2 agent minutes | 134,184 | 39,272 agent tokens |
| BG0916 | 6.4 | 13.1 agent minutes | 67,092 | 86,103 agent tokens |
| BG0917 | 6.4 | 2.4 agent minutes | 67,092 | 14,624 agent tokens |
| BG0918 | 6.4 | 2.4 agent minutes | 67,092 | 14,623 agent tokens |
| BG0919 | 6.4 | 5.9 agent minutes | 67,092 | 48,358 agent tokens |
| BG0920 | 6.4 | 9.5 agent minutes | 67,092 | 89,637 agent tokens |
| BG0925 | 6.4 | 7.0 agent minutes | 67,092 | 50,251 agent tokens |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 30 | 45 |
| Delivered of the plan | 30 | 45 |
| Added mid-run and delivered | 7 of 7 added | 8 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 53.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0911 | 2 | 2 | delivered | 2 |
| BG0912 | 2 | 2 | delivered | 1 |
| BG0913 | 2 | 2 | delivered - discharged after it was carried at the review cap: BG0923 | 3 |
| BG0898 | 2 | 2 | delivered | 2 |
| BG0899 | 1 | 1 | delivered | 1 |
| BG0900 | 1 | 1 | delivered | 2 |
| BG0901 | 1 | 1 | delivered | 1 |
| BG0903 | 1 | 1 | delivered | 2 |
| BG0904 | 1 | 1 | delivered | 1 |
| BG0908 | 2 | 2 | delivered | 1 |
| BG0907 | 2 | 2 | delivered | 2 |
| BG0914 | 1 | 1 | delivered | 2 |
| BG0905 | 1 | 1 | delivered | 1 |
| BG0906 | 1 | 1 | delivered | 1 |
| BG0910 | 1 | 1 | delivered | 1 |
| US0982 | 1 | 1 | delivered | 1 |
| BG0870 | 2 | 2 | delivered | 1 |
| BG0871 | 2 | 2 | delivered | 1 |
| BG0872 | 2 | 2 | delivered | 1 |
| BG0873 | 2 | 2 | delivered | 1 |
| BG0878 | 3 | 3 | delivered | 1 |
| BG0882 | 2 | 2 | delivered | 1 |
| BG0902 | 1 | 1 | delivered | 1 |
| BG0885 | 2 | 2 | delivered - discharged after it was carried at the review cap: BG0928 | 3 |
| US0981 | 1 | 1 | delivered | 1 |
| BG0886 | 1 | 1 | delivered | 1 |
| BG0887 | 1 | 1 | delivered | 1 |
| BG0888 | 1 | 1 | delivered | 1 |
| BG0889 | 2 | 2 | delivered | 1 |
| BG0896 | 1 | 1 | delivered | 1 |
| BG0915 | 2 | 2 | added - BG0908's remainder, split under D0316; on-goal and built in lane A2 beside the BG0912 repair; delivered | 1 |
| BG0916 | 1 | 1 | added - filed from a lane A1 round-1 low under D0317; on-goal, built after the A1 repairs; delivered | 2 |
| BG0917 | 1 | 1 | added - filed from a lane A1 round-1 low under D0317; on-goal, built after the A1 repairs; delivered | 1 |
| BG0918 | 1 | 1 | added - filed from a lane A1 round-1 low under D0317; on-goal, built after the A1 repairs; delivered | 1 |
| BG0919 | 1 | 1 | added - the round-trip gap the BG0900 review found, in the three other marks this run added (D0320); delivered | 1 |
| BG0920 | 1 | 1 | added - the checklist cost row the BG0916 review found disagreeing with the re-filed page; on-goal (D0321); delivered | 1 |
| BG0925 | 1 | 1 | added - a regression the BG0896 review found (a fenced bare command no longer named); repaired in this run (D0324); delivered | 1 |

## Known issues handed over

5 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0926 | Medium | A lane return between the close and the sign records into the run and invalidates the page before it is signed - not-stop-ship, ruled by Claude (orchestrator) |
| BG0921 | Low | The goal-review refusal still names a 'role' key after the help names 'seat' - not-stop-ship, ruled by Claude (orchestrator) |
| BG0922 | Low | The goal-note check names an unrelated 'Nx' figure as a contradiction and misses 1.7X and the multiplication sign - not-stop-ship, ruled by Claude (orchestrator) |
| BG0924 | Low | The report says no unit carries a measured time when units carry minutes but none has a forecast - not-stop-ship, ruled by Claude (orchestrator) |
| BG0927 | Low | A broken transcript in another project's folder crashes the long-path transcript scan - not-stop-ship, ruled by Claude (orchestrator) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-10-03T11:09:38Z | 24f98f9dc36eb7f6 |

Signing records the principal, the date and this report's fingerprint against RUN-01M3ZAGE.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 1,366,401 |

Total 7,753,004, of which delegated 6,386,603. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 72 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 72 commit(s) on main inside the run window |
| Lead time for changes | 5h 49m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 72 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 67,092 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 10 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

12 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| message-refs | 3 | 0 | 3 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |
| stamps-staged | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| style | 6 | 6 | 0 | 7 candidate catch(es) over 3 runs |
| unit-tests | 1 | 1 | 0 | 3 candidate catch(es) over 3 runs |

### Lessons

7 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-005 | repair breaks its neighbour | graduating (CR0608) | 1 | 4 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-013 | suite verdict before the commit | active | 0 | 0 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | active | 1 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 0 |
