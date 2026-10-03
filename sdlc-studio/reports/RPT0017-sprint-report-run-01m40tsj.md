# Sprint Report: RUN-01M40TSJ

## Goal

Maya installs v6.1.0 and every page she reads, from release notes to sprint report, matches the code.

**Verdict: Judged achieved** - Every unit of the batch, release paperwork and the pre-tag fixes included, was delivered and approved by an independent reviewer who ran each paperwork claim against the code; v6.1.0 is cut and waits on the signature and the release gate.

> **Run:** 2026-10-03T12:06:32Z to 2026-10-03T15:29:09Z (3.4h)
> **Verified on:** a1beba585561f89fc0a583a62077d4ca3bcc386e   **Fingerprint:** e84a8b047651037c

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 27 | 27 | 1.0x | 18 of 18 delivered unit(s) |
| Minutes | 164.9 | 180.3 | 1.09x | measured active minutes (spans or agent minutes) against their forecast, over the 18 of 18 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 202.6 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Tokens | 2,165,076 | 4,429,569 | 2.05x | the whole run: forecast over 18 of 18 unit(s) planned or added and not dropped; actual is the main-thread meter plus 26 delegated agent(s)' reported totals, split in the appendix |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0926 | 6.1 | 4.5 agent minutes | 80,188 | 38,173 agent tokens |
| BG0927 | 6.1 | 2.9 agent minutes | 80,188 | 24,292 agent tokens |
| BG0924 | 6.1 | 3.0 agent minutes | 80,188 | 25,449 agent tokens |
| BG0921 | 6.1 | 4.7 agent minutes | 80,188 | 39,330 agent tokens |
| BG0922 | 6.1 | 8.5 agent minutes | 80,188 | 75,478 agent tokens |
| BG0930 | 6.1 | 3.2 agent minutes | 80,188 | 26,604 agent tokens |
| BG0929 | 12.2 | 16.3 agent minutes | 160,376 | 167,165 agent tokens |
| US0984 | 18.4 | 23.7 agent minutes | 240,564 | 241,244 agent tokens |
| US0983 | 18.4 | 7.4 agent minutes | 240,564 | 74,079 agent tokens |
| US0985 | 12.2 | 32.3 agent minutes | 160,376 | 241,299 agent tokens |
| BG0931 | 12.2 | 5.7 agent minutes | 160,376 | 52,826 agent tokens |
| BG0932 | 6.1 | 2.8 agent minutes | 80,188 | 26,413 agent tokens |
| BG0933 | 6.1 | 5.7 agent minutes | 80,188 | 52,826 agent tokens |
| BG0934 | 6.1 | 10.3 agent minutes | 80,188 | 97,378 agent tokens |
| BG0935 | 6.1 | 3.3 agent minutes | 80,188 | 34,197 agent tokens |
| BG0936 | 12.2 | 12.0 agent minutes | 160,376 | 113,545 agent tokens |
| BG0937 | 6.1 | 13.6 agent minutes | 80,188 | 112,855 agent tokens |
| BG0938 | 12.2 | 20.4 agent minutes | 160,376 | 186,965 agent tokens |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 10 | 16 |
| Delivered of the plan | 10 | 16 |
| Added mid-run and delivered | 8 of 8 added | 11 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 27.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0926 | 1 | 1 | delivered | 1 |
| BG0927 | 1 | 1 | delivered | 1 |
| BG0924 | 1 | 1 | delivered | 1 |
| BG0921 | 1 | 1 | delivered | 1 |
| BG0922 | 1 | 1 | delivered | 2 |
| BG0930 | 1 | 1 | delivered | 1 |
| BG0929 | 2 | 2 | delivered | 2 |
| US0984 | 3 | 3 | delivered | 2 |
| US0983 | 3 | 3 | delivered | 1 |
| US0985 | 2 | 2 | delivered | 2 |
| BG0931 | 2 | 2 | added - found in the run and fixed in it (D0326, D0331); delivered | 1 |
| BG0932 | 1 | 1 | added - found in the run and fixed in it (D0326, D0331); delivered | 1 |
| BG0933 | 1 | 1 | added - found in the run and fixed in it (D0326, D0331); delivered | 1 |
| BG0934 | 1 | 1 | added - found in the run and fixed in it (D0326, D0331); delivered | 2 |
| BG0935 | 1 | 1 | added - found by the US0983 review and fixed in the run (D0326, D0332); delivered | 1 |
| BG0936 | 2 | 2 | added - the v6.1 review residue, fixed in the run (D0326, D0333); delivered | 1 |
| BG0937 | 1 | 1 | added - pre-tag fix under D0334 and D0335; delivered | 1 |
| BG0938 | 2 | 2 | added - pre-tag fix under D0334 and D0335; delivered | 2 |

## Known issues handed over

0 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

No open finding, close gap or carried unit is recorded.

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M40TSJ.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 569,078 |

Total 4,429,569, of which delegated 3,860,491. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 1 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 37133734434 - 1 push-triggered run(s) on main in the run window |
| Lead time for changes | 4h 21m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 44 commit(s) |
| Change failure rate | 100% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 37133734434 - 1 deployment(s); 1 failed on 125cc8f92044f91081ef91f293b68eb8ad7e95cb |
| Time to restore | not restored | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 37133734434 - main went red at run 37133734434, and no push-triggered run created after it concluded success in the run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 80,188 | velocity-record |
| Minutes per point | 6.12 | fallback: 1 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028, RETRO0131 |

### Rulings

Persona seats ruled 5 time(s), 0 of them by citing a
precedent; the operator ruled 1 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

1 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| markdown | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| neutrality | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |
| style | 0 | 0 | 0 | 7 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

7 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-005 | repair breaks its neighbour | graduating (CR0608) | 1 | 5 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | active | 0 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 0 |
| LC-018 | a doc claim checked by reading | active | 0 | 0 |
