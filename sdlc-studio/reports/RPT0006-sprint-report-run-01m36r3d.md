# Sprint Report: RUN-01M36R3D

## Goal

A sprint runs start to finish on its own, learns from itself, and hands you one page.

**Verdict: Judged achieved** - The run went from plan approval to this page without asking the operator anything: four seat rulings (D0256-D0259) answered its questions, each unit had one independent reviewer under the new cap, and the close ran in one pass. It learns from itself through a calibrated token rate measured from its own history and through ruling precedent; lesson graduation was scoped to Sprint 2 from the start.

> **Run:** 2026-09-23T09:10:21Z to open (8.1h)
> **Verified on:** 4af3dfbc3182a20daea6c4864f7c0b1cd39b9a74   **Fingerprint:** 8ce8051d2635b26f

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 58 | 58 | 1.0x | 11 of 11 delivered unit(s) |
| Minutes | NOT MEASURED - the plan recorded no minute forecast for any unit | 483.9 | NOT MEASURED - needs both a forecast and an actual | the whole run: forecast over 0 of 11 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 5,661,095 | 6,411,344 | 1.13x | the whole run: the plan's run-level token forecast; actual is the main-thread meter plus 21 delegated agent(s)' reported totals, split in the appendix |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 11 | 58 |
| Delivered of the plan | 11 | 58 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 58.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US0868 | 3 | 3 | delivered | 1 |
| US0869 | 5 | 5 | delivered | 2 |
| US0870 | 3 | 3 | delivered | 1 |
| US0871 | 5 | 5 | delivered | 2 |
| US0872 | 8 | 8 | delivered | 2 |
| US0873 | 3 | 3 | delivered | 2 |
| US0874 | 5 | 5 | delivered | 2 |
| US0875 | 8 | 8 | delivered | 2 |
| US0876 | 8 | 8 | delivered | 2 |
| US0877 | 5 | 5 | delivered | 2 |
| US0878 | 5 | 5 | delivered | 2 |

## Known issues handed over

6 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0744 | High | the close refuses to file a report but a direct build --write files one anyway, skipping the token stamp and the gate verdicts the refusal protects |
| BG0745 | High | sprint_report check reads a report hand-edited after signing as VALID |
| BG0746 | Medium | The spec-claims timing claim deadlocks every fresh worktree under parallel load |
| BG0747 | Medium | The evidence-drift lane still enforces mutation evidence that D0255 switched off, and re-registration drops other rows |
| BG0748 | Medium | The report's DORA window is second-resolution, so a same-second commit reads the report INVALID |
| BG0749 | Medium | Thirty stamped criteria on older units point at tests this sprint made skipped stubs |
| checklist | close gap | tick-verification: Ticked criteria the tree supports - no ticked criteria found |

## Sign-off

| Reviewer of record | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M36R3D.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 1,684,819 |

Total 6,411,344, of which delegated 4,726,525. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 11 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 11 commit(s) on main inside the run window |
| Lead time for changes | 7h 22m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 11 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | NOT MEASURED - the plan snapshot records no rate | backfilled at close from the plan's own forecast log (planned 2026-09-23T09:08:54Z): the plan predates US0870, so it printed one run-level token forecast of 5,661,095 (a fixed per-sprint term plus 47,613 per point) and no per-unit or minute forecast |
| Minutes per point | NOT MEASURED - the plan snapshot records no rate | not measured: no minute forecast existed when this run was planned |

### Rulings

Persona seats ruled 4 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window
