# Sprint Report: RUN-01M3891F

## Goal

Commits clear in about a minute, and the sprint learns from repeated mistakes without being told.

**Verdict: Judged partial** - The sprint learns from repeated mistakes without being told: lessons are failure classes that count repeats from retros and cited REJECTs, reach the plan, build and review briefs, graduate to a CR on a second repeat and retire when quiet, with a bundled seed for new projects (US0887, US0888). Commits do not yet clear in about a minute: a paperwork commit clears in seconds and a push fell from about 750s to 284s, but a code commit that reaches a widely imported script still took 165-258s under this machine's load against the 90s budget (BG0754).

> **Run:** 2026-09-23T23:32:40Z to open (5.4h)
> **Verified on:** 2b08ef7b9a6f7a9ec29ed9a87c0133f375b51a35   **Fingerprint:** 898129ed43c8b31d

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 42 | 42 | 1.0x | 11 of 11 delivered unit(s) |
| Minutes | 268.8 | 325.0 | 1.21x | the whole run: forecast over 11 of 11 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 14,860,020 | 7,459,811 | 0.5x | the whole run: forecast over 11 of 11 unit(s) planned or added and not dropped; actual is the main-thread meter plus 36 delegated agent(s)' reported totals, split in the appendix |

Each unit's minutes and tokens are measured over its own open span. Units open at the same time
share hours and tokens, so these spans may overlap and are never added up into the run's figures
above.

| Unit | Forecast minutes | Minutes (open span) | Forecast tokens | Tokens (open span) |
| --- | --- | --- | --- | --- |
| US0879 | 32.0 | 152.2 | 1,769,050 | 1,074,711 |
| US0880 | 32.0 | 129.9 | 1,769,050 | 434,638 |
| US0881 | 32.0 | 69.0 | 1,769,050 | 181,471 |
| US0882 | 19.2 | 81.6 | 1,061,430 | 698,581 |
| US0883 | 19.2 | 101.7 | 1,061,430 | 754,471 |
| US0884 | 19.2 | 86.6 | 1,061,430 | 692,968 |
| US0885 | 12.8 | 21.9 | 707,620 | 88,505 |
| US0886 | 19.2 | 36.6 | 1,061,430 | 139,545 |
| US0887 | 32.0 | 203.5 | 1,769,050 | 1,173,880 |
| US0888 | 32.0 | 166.8 | 1,769,050 | 1,026,508 |
| US0889 | 19.2 | 85.5 | 1,061,430 | 658,497 |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 11 | 42 |
| Delivered of the plan | 11 | 42 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 42.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US0879 | 5 | 5 | delivered | 1 |
| US0880 | 5 | 5 | delivered | 1 |
| US0881 | 5 | 5 | delivered | 1 |
| US0882 | 3 | 3 | delivered | 2 |
| US0883 | 3 | 3 | delivered | 2 |
| US0884 | 3 | 3 | delivered | 1 |
| US0885 | 2 | 2 | delivered | 1 |
| US0886 | 3 | 3 | delivered | 1 |
| US0887 | 5 | 5 | delivered | 2 |
| US0888 | 5 | 5 | delivered | 2 |
| US0889 | 3 | 3 | delivered | 1 |

## Known issues handed over

5 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0750 | Medium | A same-day waiver flips a filed sprint report INVALID |
| BG0751 | Medium | Open findings in a sprint report use an inclusive window end |
| BG0752 | Medium | Per-commit test selection skips hooks, test infrastructure and code reached through another script |
| BG0753 | Medium | The test suite leaks temporary directories into /tmp |
| BG0754 | Medium | A commit touching a widely imported script runs well over the 90-second budget |
| checklist | close gap | tick-verification: Ticked criteria the tree supports - no ticked criteria found |

## Sign-off

| Reviewer of record | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3891F.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 1,484,649 |

Total 7,459,811, of which delegated 5,975,162. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 15 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 15 commit(s) on main inside the run window |
| Lead time for changes | 5h 8m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 15 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 353,810 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 2 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lessons

7 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | active | 1 | 1 |
| LC-003 | mechanism reaches no caller | active | 0 | 0 |
| LC-004 | premise not executed | active | 0 | 0 |
| LC-005 | repair breaks its neighbour | active | 1 | 1 |
| LC-006 | absence read as an answer | active | 0 | 0 |
| LC-007 | shared machine resources exhausted | active | 0 | 0 |
