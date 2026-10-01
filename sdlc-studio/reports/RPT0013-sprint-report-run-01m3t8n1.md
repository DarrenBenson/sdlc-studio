# Sprint Report: RUN-01M3T8N1

## Goal

Maya signs, without a re-close, a report that checks VALID and names every operator ruling and carry

**Verdict: Judged achieved** - BG0862 runs the shipped close, retro, close, sign and check unstubbed on a schema 3 run holding a carry discharged by its rejecting reviewer (BG0850), a resolved decision and a forced override on a dropped unit (BG0851), and a lesson ruled by class (BG0849): one report, VALID first time with no unit moved by hand (BG0848, BG0859), every ruling named on the page (BG0865), retro scaffolded with its run and table (BG0826); the carried bug is now plannable (BG0829). The real proof is this close: no units were moved by hand before it.

> **Run:** 2026-09-30T23:00:50Z to open (8.1h)
> **Verified on:** 001ddc5131ca62115f49ebe230790fc9f3937c59   **Fingerprint:** 439d9fa814d6d4d2

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 29 | 29 | 1.0x | 9 of 9 delivered unit(s) |
| Minutes | 185.6 | 486.1 | 2.62x | the whole run: forecast over 9 of 9 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 5,172,208 | 2,325,464 | 0.45x | the whole run: forecast over 9 of 9 unit(s) planned or added and not dropped; actual is the run meter, a lower bound |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. Spans of
units open at the same time overlap, so no per-unit figure is added up into the run's figures
above.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0826 | 12.8 | 411.6 | 356,704 | 2,204,266 |
| BG0859 | 12.8 | 471.9 | 356,704 | 2,311,863 |
| BG0848 | 19.2 | 394.4 | 535,056 | 2,181,477 |
| BG0829 | 19.2 | 439.6 | 535,056 | 2,249,261 |
| BG0850 | 19.2 | 454.3 | 535,056 | 2,297,050 |
| BG0851 | 32.0 | 360.6 | 891,760 | 2,115,039 |
| BG0849 | 19.2 | 341.9 | 535,056 | 2,090,327 |
| BG0862 | 32.0 | 313.6 | 891,760 | 2,043,697 |
| BG0865 | 19.2 | 58.9 | 535,056 | 92,947 |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 8 | 26 |
| Delivered of the plan | 8 | 26 |
| Added mid-run and delivered | 1 of 1 added | 3 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 29.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0826 | 2 | 2 | delivered | 1 |
| BG0859 | 2 | 2 | delivered | 1 |
| BG0848 | 3 | 3 | delivered | 1 |
| BG0829 | 3 | 3 | delivered | 1 |
| BG0850 | 3 | 3 | delivered | 1 |
| BG0851 | 5 | 5 | delivered | 1 |
| BG0849 | 3 | 3 | delivered | 1 |
| BG0862 | 5 | 5 | delivered | 1 |
| BG0865 | 3 | 3 | added - Operator ruling 2026-10-01: BG0862 proved the signed page never states a non-STOP-SHIP retro ruling and a close-filed graduation CR falls outside the window, so the goal 'names every operator ruling and carry' needs this page change; added rather than rewording the goal; delivered | 1 |

## Known issues handed over

3 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0863 | Medium | An unreadable verdict ledger drops unreviewed units from the close's status rows since BG0859, and the bug remedy is wrong for a bug that already has an APPROVE - not-stop-ship, ruled by Claude (orchestrator) |
| BG0864 | Medium | transition to Fixed admits a bug whose Verify lines have never been run, so a carried bug with red or manual-only criteria reaches Fixed with nothing executed - not-stop-ship, ruled by Claude (orchestrator) |
| BG0865 | Medium | The signed page names a known issue's retro ruling only when it is STOP-SHIP, and a finding the close files falls outside the run window |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3T8N1.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 2,325,464 |

Total 2,325,464, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 5 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 36826457564/36802767721/36798908986/36794772826/36789601166 - 5 push-triggered run(s) on main in the run window |
| Lead time for changes | 7h 57m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 24 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | forge runs 36826457564/36802767721/36798908986/36794772826/36789601166 - 5 deployment(s); 0 failed on none |
| Time to restore | no restore needed | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | forge runs 36826457564/36802767721/36798908986/36794772826/36789601166 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 178,352 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 7 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |
| style | 1 | 1 | 0 | 2 candidate catch(es) over 3 runs |
| unit-tests | 2 | 2 | 0 | 2 candidate catch(es) over 3 runs |

### Lessons

12 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | graduating (CR0595) | 1 | 55 |
| LC-003 | mechanism reaches no caller | graduating (CR0598) | 0 | 9 |
| LC-004 | premise not executed | graduating (CR0600) | 0 | 2 |
| LC-005 | repair breaks its neighbour | active | 0 | 1 |
| LC-006 | absence read as an answer | graduating (CR0596) | 1 | 16 |
| LC-008 | constraint added without retirement | graduating (CR0597) | 0 | 11 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 0 |
| LC-011 | widen-after-brief | active | 0 | 0 |
| LC-012 | a reviewer's clone cannot see writes into the main repo | active | 0 | 0 |
| LC-013 | suite verdict before the commit | active | 0 | 0 |
| LC-014 | paperwork during a build | active | 0 | 0 |
