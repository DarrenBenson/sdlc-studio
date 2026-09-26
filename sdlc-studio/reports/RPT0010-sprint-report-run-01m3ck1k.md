# Sprint Report: RUN-01M3CK1K

## Goal

Maya runs the lean loop on a fresh v6 project, and the release candidate ships.

**Verdict: Judged achieved** - The lean loop runs on a fresh v6 project on the shipped defaults, plan to sign (US0950 AC3, US0951); all 37 batch units delivered under the two-round cap; the release bar is met (no open High), and v6.0.0-rc.1 is cut from this close by the release runbook before the report is signed

> **Run:** 2026-09-25T15:32:20Z to open (24.3h)
> **Verified on:** 1c404a481692986b13208ea43178d918a3275f5d   **Fingerprint:** a0ca5cb38fc2965b

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 102 | 102 | 1.0x | 37 of 37 delivered unit(s) |
| Minutes | 652.8 | 1459.0 | 2.23x | the whole run: forecast over 37 of 37 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 36,088,620 | 18,791,718 | 0.52x | the whole run: forecast over 37 of 37 unit(s) planned or added and not dropped; actual is the main-thread meter plus 73 delegated agent(s)' reported totals, split in the appendix |

Each unit's minutes and tokens are measured over its own open span. Units open at the same time
share hours and tokens, so these spans may overlap and are never added up into the run's figures
above.

| Unit | Forecast minutes | Minutes (open span) | Forecast tokens | Tokens (open span) |
| --- | --- | --- | --- | --- |
| US0937 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0771 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0772 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0914 | 51.2 | NOT MEASURED - not recorded | 2,830,480 | NOT MEASURED - not recorded |
| US0925 | 32.0 | NOT MEASURED - not recorded | 1,769,050 | NOT MEASURED - not recorded |
| US0939 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0936 | 51.2 | NOT MEASURED - not recorded | 2,830,480 | NOT MEASURED - not recorded |
| US0922 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0919 | 32.0 | NOT MEASURED - not recorded | 1,769,050 | NOT MEASURED - not recorded |
| US0918 | 32.0 | NOT MEASURED - not recorded | 1,769,050 | NOT MEASURED - not recorded |
| US0923 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0950 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0938 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0940 | 32.0 | NOT MEASURED - not recorded | 1,769,050 | NOT MEASURED - not recorded |
| US0942 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0943 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| US0944 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0945 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| US0946 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| US0947 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0948 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0949 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| US0951 | 32.0 | NOT MEASURED - not recorded | 1,769,050 | NOT MEASURED - not recorded |
| BG0681 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0687 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0695 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0711 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0731 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0717 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0773 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| BG0775 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| BG0779 | 6.4 | NOT MEASURED - not recorded | 353,810 | NOT MEASURED - not recorded |
| BG0778 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0780 | 19.2 | NOT MEASURED - not recorded | 1,061,430 | NOT MEASURED - not recorded |
| BG0777 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0781 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |
| BG0787 | 12.8 | NOT MEASURED - not recorded | 707,620 | NOT MEASURED - not recorded |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 31 | 92 |
| Delivered of the plan | 29 | 84 |
| Added mid-run and delivered | 8 of 8 added | 18 |
| Dropped | 2 | 8 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 102.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US0937 | 1 | 1 | delivered | 2 |
| BG0771 | 1 | 1 | delivered | 1 |
| BG0772 | 3 | 3 | delivered | 2 |
| BG0755 | 3 | 3 | dropped - carried at the review cap: BG0773 | 2 |
| US0914 | 8 | 8 | delivered | 2 |
| US0925 | 5 | 5 | delivered | 2 |
| US0939 | 2 | 2 | delivered | 1 |
| US0936 | 8 | 8 | delivered | 1 |
| US0922 | 2 | 2 | delivered | 1 |
| US0919 | 5 | 5 | delivered | 2 |
| US0918 | 5 | 5 | delivered | 2 |
| US0923 | 3 | 3 | delivered | 1 |
| US0950 | 3 | 3 | delivered | 1 |
| US0938 | 3 | 3 | delivered | 2 |
| US0940 | 5 | 5 | delivered | 2 |
| US0941 | 5 | 5 | dropped - carried at the review cap: BG0775 | 2 |
| US0942 | 3 | 3 | delivered | 2 |
| US0943 | 1 | 1 | delivered | 1 |
| US0944 | 2 | 2 | delivered | 2 |
| US0945 | 3 | 3 | delivered | 2 |
| US0946 | 1 | 1 | delivered | 2 |
| US0947 | 2 | 2 | delivered | 1 |
| US0948 | 2 | 2 | delivered | 1 |
| US0949 | 2 | 2 | delivered | 2 |
| US0951 | 5 | 5 | delivered | 1 |
| BG0681 | 1 | 1 | delivered | 1 |
| BG0687 | 2 | 2 | delivered | 1 |
| BG0695 | 1 | 1 | delivered | 1 |
| BG0711 | 1 | 1 | delivered | 1 |
| BG0731 | 2 | 2 | delivered | 2 |
| BG0717 | 2 | 2 | delivered | 1 |
| BG0773 | 3 | 3 | added - carries BG0755 at the review cap; its one-line fix restores US0081's full-template selection; delivered | 1 |
| BG0775 | 3 | 3 | added - carries US0941 (never-cut, D0275) at the review cap; closes two anchor bypasses the round-2 review found; delivered | 2 |
| BG0779 | 1 | 1 | added - US0945's advisory is invisible on a passing commit; the story's title promises it before the commit lands; delivered | 1 |
| BG0778 | 2 | 2 | added - fresh v6 projects are schema v3; the retro drops their ULID ids, the same class US0951 fixed for the Batch; delivered | 2 |
| BG0780 | 3 | 3 | added - US0948 made the lock fail closed; its QA review found a non-busy flock error now fails every write, and three callers mishandle the timeout; delivered | 1 |
| BG0777 | 2 | 2 | added - BG0687 made verify_ac run every Verify line; the lane runner and revert check still read the first, a false green on a stacked block; delivered | 1 |
| BG0781 | 2 | 2 | added - BG0780's QA review: a busy lock as EACCES fails at once (regression on SMB mounts) and two warnings invite a duplicate filing; delivered | 1 |
| BG0787 | 2 | 2 | added - A High: RPT0009, the last signed report, reads INVALIDATED; rc.1's bar is zero open High; delivered | 2 |

## Known issues handed over

10 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0599 | High | The sprint signature is recorded in a tracked file, so any clone can verify a signed report |
| BG0774 | Medium | install.sh exits 1 after a successful install when the gemini target is chosen without the gemini CLI |
| BG0776 | Medium | sprint sign --principal - seals the run with an empty principal |
| BG0782 | Medium | About 57 test modules commit in a temporary git repo with auto-maintenance on, the race BG0711 fixed in one |
| BG0783 | Medium | Review rounds are write-dead after US0918, so the ceiling and repair-regression readers of run-state rounds read nothing |
| BG0784 | Medium | A seat card with no role line is silently bypassed for the shipped card, and the unknown-seat refusal names the wrong seats |
| BG0785 | Medium | migrate leaves a v4-era project's conformance lane red on its pre-adoption stories and names no cutoff for them |
| BG0786 | Medium | flow.py compute takes about 90 seconds on this repository, so its CLI grammar control times out at 120 under load and reddens the push gate |
| BG0788 | Medium | Signed-report rounds are positional, so a hand-deleted verdict row goes unseen when a same-day later run re-reviewed the unit, and verdict rows carry no run id |
| CR0600 | Medium | Prevent or retire lesson LC-004 (premise not executed) |

## Sign-off

| Reviewer of record | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3CK1K.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 4,503,299 |

Total 18,791,718, of which delegated 14,288,419. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 61 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 61 commit(s) on main inside the run window |
| Lead time for changes | 23h 59m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 61 commit(s) |
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

### Lane yield

9 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 2 | 1 | 1 | 1 candidate catch(es) over 3 runs |
| message-refs | 5 | 0 | 5 | delete candidate: 5 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |

### Lessons

12 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | graduating (CR0595) | 16 | 37 |
| LC-003 | mechanism reaches no caller | graduating (CR0598) | 4 | 6 |
| LC-004 | premise not executed | graduating (CR0600) | 1 | 2 |
| LC-005 | repair breaks its neighbour | active | 0 | 1 |
| LC-006 | absence read as an answer | graduating (CR0596) | 4 | 10 |
| LC-007 | shared machine resources exhausted | active | 0 | 0 |
| LC-008 | constraint added without retirement | graduating (CR0597) | 1 | 9 |
| LC-009 | the review cap carries trivial fixes | active | 0 | 0 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 0 |
| LC-011 | widen-after-brief | active | 0 | 0 |
| LC-012 | a reviewer's clone cannot see writes into the main repo | active | 0 | 0 |

### Not measured

Close checklist rows this run gave nothing to measure. Nothing is known to be wrong, so none is
a known issue; nothing is known to be right, so none reads as done.

| Row | State | Why |
| --- | --- | --- |
| cost: Cost, velocity and estimate accuracy | not measured | no per-unit telemetry and no harness-tracked sprint total, so what this sprint cost is not attributable - which is not zero |
