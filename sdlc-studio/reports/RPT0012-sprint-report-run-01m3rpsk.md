# Sprint Report: RUN-01M3RPSK

## Goal

Jonah's team installs v6 via Claude Code or Copilot CLI; migrate predicts the gate's reconcile, conformance, validate and floor failures

**Verdict: Judged achieved** - Copilot CLI now installs globally and is hinted only when no folder it reads holds a copy (BG0852 via BG0856); on a committed v4.1-shaped project migrate names reconcile 2, conformance 3, validate 4 and engagement-floor 2 exactly as gate.py then fails them (BG0854, over BG0842/43/44/45); seeded AGENTS.md names the skill through <skill> (BG0853). Disclosed: a schema v3 project whose conformance failures are ULID-only is not yet named (BG0858).

> **Run:** 2026-09-30T08:17:59Z to open (4.4h)
> **Verified on:** 7bff58aac5f5329e62c8c9c1f5e25f12e716a06a   **Fingerprint:** 341149404ed2af89

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 18 | 18 | 1.0x | 7 of 7 delivered unit(s) |
| Minutes | 115.2 | 261.6 | 2.27x | the whole run: forecast over 7 of 7 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 3,210,336 | 971,934 | 0.3x | the whole run: forecast over 7 of 7 unit(s) planned or added and not dropped; actual is the run meter, a lower bound |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. Spans of
units open at the same time overlap, so no per-unit figure is added up into the run's figures
above.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0842 | 12.8 | 0.0 | 356,704 | 0 |
| BG0844 | 12.8 | 0.0 | 356,704 | 0 |
| BG0843 | 19.2 | 0.0 | 535,056 | 0 |
| BG0845 | 19.2 | 0.0 | 535,056 | 0 |
| BG0853 | 19.2 | 0.0 | 535,056 | 0 |
| BG0854 | 19.2 | 0.0 | 535,056 | 0 |
| BG0856 | 12.8 | 0.0 | 356,704 | 0 |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 7 | 21 |
| Delivered of the plan | 6 | 16 |
| Added mid-run and delivered | 1 of 1 added | 2 |
| Dropped | 1 | 5 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 18.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0842 | 2 | 2 | delivered | 1 |
| BG0844 | 2 | 2 | delivered | 1 |
| BG0843 | 3 | 3 | delivered | 1 |
| BG0845 | 3 | 3 | delivered | 1 |
| BG0853 | 3 | 3 | delivered | 2 |
| BG0854 | 3 | 3 | delivered | 1 |
| BG0852 | 5 | 5 | dropped - carried at the review cap: BG0856 | 2 |
| BG0856 | 2 | 2 | added - Operator ruling 2026-09-30: BG0852 was carried at the review cap; its findings in BG0856 are groomed and delivered in this run as a fresh unit rather than a third review round; delivered | 2 |

## Known issues handed over

6 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0856 | Medium | BG0852 did not converge in review: round 2 REJECT findings |
| BG0857 | Medium | An unreadable epics directory is read as absence by reconcile's detectors, so the gate and migrate report a drift count with no mention that part of the workspace was never read |
| BG0858 | Medium | migrate names nothing when the conformance lane fails only on ULID-id units or repo-wide failures, so a schema v3 project meets the failure at the gate unannounced |
| BG0859 | Medium | The close's status preflight stops every approved bug left In Progress and tells the operator to move it to Review, a status bugs do not have |
| BG0860 | Medium | A sprint plan preview with no --write appends forecast rows to the tracked evidence log, so each dry run adds a duplicate forecast per unit |
| BG0861 | Medium | Nothing opens a delivery batch since US0918, so every finding is stamped raised outside a batch and the close's finding-placement figure is always empty |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3RPSK.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 971,934 |

Total 971,934, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 36710190700/36704422675/36699593318/36689796152 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 4h 12m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 26 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | forge runs 36710190700/36704422675/36699593318/36689796152 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | forge runs 36710190700/36704422675/36699593318/36689796152 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 178,352 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 1 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

11 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| markdown | 5 | 0 | 5 | 1 candidate catch(es) over 3 runs |
| message-refs | 3 | 0 | 3 | delete candidate: 9 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |
| style | 3 | 1 | 2 | 1 candidate catch(es) over 3 runs |

### Lessons

12 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | graduating (CR0595) | 3 | 54 |
| LC-003 | mechanism reaches no caller | graduating (CR0598) | 1 | 9 |
| LC-004 | premise not executed | graduating (CR0600) | 0 | 2 |
| LC-005 | repair breaks its neighbour | active | 0 | 1 |
| LC-006 | absence read as an answer | graduating (CR0596) | 0 | 15 |
| LC-008 | constraint added without retirement | graduating (CR0597) | 0 | 11 |
| LC-009 | the review cap carries trivial fixes | active | 0 | 0 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 0 |
| LC-011 | widen-after-brief | active | 0 | 0 |
| LC-012 | a reviewer's clone cannot see writes into the main repo | active | 0 | 0 |
| LC-013 | suite verdict before the commit | active | 0 | 0 |
