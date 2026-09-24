# Sprint Report: RUN-01M39MC0

## Goal

A commit clears in ninety seconds, and every commit lane left standing shows what it caught.

**Verdict: Judged partial** - Half one missed by 3s: a one-line gate.py commit measured 93s end to end against 90 (229s at the start), with its suites down to 43s; code commits this run cleared in 60-75s. The rest is the sequential pre-commit, as US0891 was carried (BG0759). Half two not delivered: US0904's lane-yield log was carried at the review cap on a one-character defect (BG0761). Deleted: the warning ratchet, verify ratchet, boundary roster and release-notes count pin, plus eight advisory lanes off the commit.

> **Run:** 2026-09-24T12:03:22Z to open (7.2h)
> **Verified on:** 9169d40340f57dbeaa6c2f9e3bd79275719a4d21   **Fingerprint:** ed21330f92c071cb

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 32 | 32 | 1.0x | 16 of 16 delivered unit(s) |
| Minutes | 204.8 | 429.5 | 2.1x | the whole run: forecast over 16 of 16 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 11,321,920 | 11,644,284 | 1.03x | the whole run: forecast over 16 of 16 unit(s) planned or added and not dropped; actual is the main-thread meter plus 72 delegated agent(s)' reported totals, split in the appendix |

Each unit's minutes and tokens are measured over its own open span. Units open at the same time
share hours and tokens, so these spans may overlap and are never added up into the run's figures
above.

| Unit | Forecast minutes | Minutes (open span) | Forecast tokens | Tokens (open span) |
| --- | --- | --- | --- | --- |
| BG0742 | 19.2 | 23.7 | 1,061,430 | 189,663 |
| US0890 | 6.4 | 15.6 | 353,810 | 122,446 |
| US0892 | 12.8 | 34.3 | 707,620 | 285,936 |
| US0893 | 12.8 | 42.1 | 707,620 | 222,951 |
| US0894 | 6.4 | 19.8 | 353,810 | 158,771 |
| US0895 | 12.8 | 53.6 | 707,620 | 147,555 |
| US0896 | 12.8 | 51.0 | 707,620 | 378,351 |
| US0897 | 12.8 | 37.4 | 707,620 | 302,974 |
| US0898 | 12.8 | 42.5 | 707,620 | 447,162 |
| US0899 | 19.2 | 63.7 | 1,061,430 | 73,981 |
| US0901 | 19.2 | 61.8 | 1,061,430 | 322,498 |
| US0902 | 6.4 | 28.9 | 353,810 | 281,837 |
| US0903 | 6.4 | 19.0 | 353,810 | 266,316 |
| US0906 | 12.8 | 19.8 | 707,620 | 245,682 |
| US0907 | 19.2 | 57.3 | 1,061,430 | 275,433 |
| US0908 | 12.8 | 36.0 | 707,620 | 274,413 |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 21 | 45 |
| Delivered of the plan | 16 | 32 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 5 | 13 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 32.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0742 | 3 | 3 | delivered | 1 |
| BG0754 | 5 | 5 | dropped - Not delivered: its AC2 needs US0891, which was carried at the review cap (BG0759), and AC1 measured 93s against 90 at the close. It stays Open, ruled deferred in RETRO0123, and closes when BG0759 lands. | 0 |
| US0890 | 1 | 1 | delivered | 1 |
| US0891 | 3 | 3 | dropped - carried at the review cap: BG0759 | 2 |
| US0892 | 2 | 2 | delivered | 2 |
| US0893 | 2 | 2 | delivered | 1 |
| US0894 | 1 | 1 | delivered | 1 |
| US0895 | 2 | 2 | delivered | 1 |
| US0896 | 2 | 2 | delivered | 2 |
| US0897 | 2 | 2 | delivered | 1 |
| US0898 | 2 | 2 | delivered | 2 |
| US0899 | 3 | 3 | delivered | 2 |
| US0900 | 1 | 1 | dropped - carried at the review cap: BG0756 | 2 |
| US0901 | 3 | 3 | delivered | 2 |
| US0902 | 1 | 1 | delivered | 1 |
| US0903 | 1 | 1 | delivered | 2 |
| US0904 | 3 | 3 | dropped - carried at the review cap: BG0761 | 2 |
| US0905 | 1 | 1 | dropped - carried at the review cap: BG0760 | 2 |
| US0906 | 2 | 2 | delivered | 1 |
| US0907 | 3 | 3 | delivered | 2 |
| US0908 | 2 | 2 | delivered | 2 |

## Known issues handed over

15 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0750 | Medium | A same-day waiver flips a filed sprint report INVALID |
| BG0751 | Medium | Open findings in a sprint report use an inclusive window end |
| BG0752 | Medium | Per-commit test selection skips hooks, test infrastructure and code reached through another script |
| BG0753 | Medium | The test suite leaks temporary directories into /tmp |
| BG0754 | Medium | A commit touching a widely imported script runs well over the 90-second budget |
| BG0755 | Medium | artifact.py batch ignores a story's role, capability and benefit, and its default template leaves a page of placeholders |
| BG0756 | Medium | US0900 did not converge in review: round 2 REJECT findings |
| BG0757 | Medium | repo_map.py build crashes on Python 3.10 when a source file holds a null byte |
| BG0758 | Medium | command_audit._surface_module reuses whatever surface module the process already imported |
| BG0759 | Medium | US0891 did not converge in review: round 2 REJECT findings |
| BG0760 | Medium | US0905 did not converge in review: round 2 REJECT findings |
| BG0761 | Medium | US0904 did not converge in review: round 2 REJECT findings |
| CR0595 | Medium | Prevent or retire lesson LC-002 (criterion words outrun the fixture) |
| CR0596 | Medium | Prevent or retire lesson LC-006 (absence read as an answer) |
| CR0597 | Medium | Prevent or retire lesson LC-008 (constraint added without retirement) |

## Sign-off

| Reviewer of record | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-09-24T20:56:51Z | ed21330f92c071cb |

Signing records the principal, the date and this report's fingerprint against RUN-01M39MC0.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 1,875,585 |

Total 11,644,284, of which delegated 9,768,699. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 23 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 23 commit(s) on main inside the run window |
| Lead time for changes | 6h 43m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 23 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 353,810 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 3 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lessons

9 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | graduating (CR0595) | 8 | 9 |
| LC-003 | mechanism reaches no caller | active | 1 | 1 |
| LC-004 | premise not executed | active | 0 | 0 |
| LC-005 | repair breaks its neighbour | active | 0 | 1 |
| LC-006 | absence read as an answer | graduating (CR0596) | 2 | 2 |
| LC-007 | shared machine resources exhausted | active | 0 | 0 |
| LC-008 | constraint added without retirement | graduating (CR0597) | 4 | 4 |
| LC-009 | the review cap carries trivial fixes | active | 0 | 0 |
