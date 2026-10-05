# Sprint Report: RUN-01M45FV6

## Goal

Maya signs only a report that still checks VALID, and config show reads every shipped default.

**Verdict: Judged achieved** - Both units delivered and approved in their first review: sign refuses a filed page that no longer re-derives, and config show reads every shipped default; the review Lows are filed under D0338

> **Run:** 2026-10-05T07:21:58Z to 2026-10-05T07:59:38Z (0.6h)
> **Verified on:** 87d80a6064f5e2ec7d4a974787591ecebfc9548a   **Fingerprint:** 4b8303e43a18d849

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 3 | 3 | 1.0x | 2 of 2 delivered unit(s) |
| Minutes | 19.2 | 16.7 | 0.87x | measured active minutes (spans or agent minutes) against their forecast, over the 2 of 2 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 37.7 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Tokens | 398,100 | 558,755 | 1.4x | the whole run: forecast over 2 of 2 unit(s) planned or added and not dropped; actual is the main-thread meter plus 5 delegated agent(s)' reported totals, split in the appendix |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0940 | 12.8 | 12.2 agent minutes | 265,400 | 124,372 agent tokens |
| BG0943 | 6.4 | 4.5 agent minutes | 132,700 | 46,640 agent tokens |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 2 | 3 |
| Delivered of the plan | 2 | 3 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 3.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0940 | 2 | 2 | delivered | 1 |
| BG0943 | 1 | 1 | delivered | 1 |

## Known issues handed over

2 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0944 | Low | Three behaviours BG0940 and BG0943 shipped have no test that fails when they break - not-stop-ship, ruled by orchestrator |
| BG0945 | Low | BG0940's changelog entry says a page with a late ruling is signed, though sign refuses until the run is re-closed - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-10-05T08:13:39Z | 4b8303e43a18d849 |

Signing records the principal, the date and this report's fingerprint against RUN-01M45FV6.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 102,720 |

Total 558,755, of which delegated 456,035. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 5 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 5 commit(s) on main inside the run window |
| Lead time for changes | 0h 19m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 5 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 132,700 | velocity-record |
| Minutes per point | 6.4 | fallback: 2 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028, RETRO0131, RETRO0132 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| neutrality | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |
| style | 1 | 1 | 0 | 8 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | active | 0 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 0 |
| LC-018 | a doc claim checked by reading | active | 0 | 0 |
