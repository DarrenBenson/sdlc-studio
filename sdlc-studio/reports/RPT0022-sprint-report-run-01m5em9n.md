# Sprint Report: RUN-01M5EM9N

## Goal

Reviewers see only self-checked work, a run's real cost is measured and held to budget, and 6.2's blockers are fixed

**Verdict: Judged partial** - The self-check gate, the priced cost meter and the regression flag shipped and hold on main; 6.2's blockers (BG0963 and the rest) moved to run four, and the run's own cost per point did not improve.

> **Run:** 2026-10-21T07:13:22Z to 2026-10-28T00:09:55Z (160.9h)
> **Verified on:** 8e7430f4b1b14edb9c2c061be3912b33abecdef6   **Fingerprint:** ebea81ff8c27f180

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 55 | 55 | 1.0x | 19 of 19 delivered unit(s) |
| Minutes | 321.1 | NOT MEASURED - no unit carries a measured time (an In Progress span or agent minutes) | NOT MEASURED - needs both a forecast and an actual | the whole run: forecast over 19 of 19 unit(s) planned or added and not dropped; no unit carries both a forecast and a measured time |
| Wall-clock span | not forecast | 9656.5 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 156,411,346 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 37,014,716 (input 10,546 x1, output 1,099,067 x5, cache write 5m 33,754,245 x1.25, cache write 1h 2,150,858 x2, cache read 1,044,109,430 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; 2 reading(s) taken on an earlier counting basis were re-derived from the transcript, up to the moment each was taken, under the current one |
| Tokens | 10,243,860 | 37,014,716 | 3.61x | the whole run: forecast over 19 of 19 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading; 2 reading(s) taken on an earlier counting basis were re-derived from the transcript, up to the moment each was taken, under the current one |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG1000 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1000 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1000 --delegated-minutes M` |
| US1087 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1087 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1087 --delegated-minutes M` |
| US1088 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1088 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1088 --delegated-minutes M` |
| US1089 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1089 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1089 --delegated-minutes M` |
| US1090 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1090 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1090 --delegated-minutes M` |
| BG1078 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1078 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1078 --delegated-minutes M` |
| BG1095 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1095 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1095 --delegated-minutes M` |
| BG0962 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0962 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0962 --delegated-minutes M` |
| BG1111 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1111 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1111 --delegated-minutes M` |
| US1091 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1091 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1091 --delegated-minutes M` |
| US1092 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1092 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1092 --delegated-minutes M` |
| US1093 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1093 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1093 --delegated-minutes M` |
| US1094 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1094 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1094 --delegated-minutes M` |
| US1095 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1095 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1095 --delegated-minutes M` |
| US1096 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1096 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1096 --delegated-minutes M` |
| BG1113 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1113 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1113 --delegated-minutes M` |
| BG1117 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1117 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1117 --delegated-minutes M` |
| US1097 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1097 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1097 --delegated-minutes M` |
| BG1127 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1127 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1127 --delegated-minutes M` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 12 | 26 |
| Delivered of the plan | 8 | 19 |
| Added mid-run and delivered | 11 of 11 added | 36 |
| Dropped | 4 | 7 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 55.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1000 | 3 | 3 | delivered | 2 |
| US1087 | 2 | 2 | delivered | 2 |
| US1088 | 3 | 3 | delivered | 2 |
| US1089 | 3 | 3 | delivered | 1 |
| US1090 | 1 | 1 | delivered | 1 |
| BG1078 | 2 | 2 | delivered | 1 |
| BG1095 | 2 | 2 | delivered | 1 |
| BG0962 | 3 | 3 | delivered | 2 |
| US1080 | 3 | 3 | dropped - D0389: moved to run four with CR0645-CR0647 and CR0649, to make room for the process-efficiency epic (CR0651) in 6.2 | 0 |
| US1081 | 2 | 2 | dropped - D0389: moved to run four with CR0645-CR0647 and CR0649, to make room for the process-efficiency epic (CR0651) in 6.2 | 0 |
| US1082 | 1 | 1 | dropped - D0389: moved to run four with CR0645-CR0647 and CR0649, to make room for the process-efficiency epic (CR0651) in 6.2 | 0 |
| US1083 | 1 | 1 | dropped - D0389: moved to run four with CR0645-CR0647 and CR0649, to make room for the process-efficiency epic (CR0651) in 6.2 | 0 |
| BG1111 | 2 | 2 | added - no reason recorded; delivered | 1 |
| US1091 | 5 | 5 | added - no reason recorded; delivered | 2 |
| US1092 | 2 | 2 | added - no reason recorded; delivered | 1 |
| US1093 | 5 | 5 | added - no reason recorded; delivered | 1 |
| US1094 | 3 | 3 | added - no reason recorded; delivered | 1 |
| US1095 | 5 | 5 | added - no reason recorded; delivered | 1 |
| US1096 | 3 | 3 | added - no reason recorded; delivered | 2 |
| BG1113 | 3 | 3 | added - no reason recorded; delivered | 1 |
| BG1117 | 3 | 3 | added - no reason recorded; delivered | 2 |
| US1097 | 3 | 3 | added - no reason recorded; delivered | 2 |
| BG1127 | 2 | 2 | added - no reason recorded; delivered | 1 |

## Known issues handed over

26 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1109 | Medium | The artefact gate's conformance and engagement-floor lanes re-read the verdict ledger, the decisions log and each verifier's collection once per unit - not-stop-ship, ruled by Darren Benson (operator) |
| BG1114 | Medium | critic.py brief spends 19 of its 20 seconds walking the artefact corpus, because it reads the files' history without the corpus cache that lane brief opens - not-stop-ship, ruled by Darren Benson (operator) |
| BG1116 | Medium | Shipped guidance tells a consuming project's agent to run the full suite before every commit, which the shipped gate's per-commit selection and push-boundary suite exist to avoid - not-stop-ship, ruled by Darren Benson (operator) |
| BG1120 | Medium | A self-check record reads an author's own edit made in a merge commit as another unit's, so the brief gate admits a changed diff in a project that merges - not-stop-ship, ruled by Darren Benson (operator) |
| BG1122 | Medium | Each meter reading now re-reads every subagent transcript from the start, so a lane, transition or report command takes about 36 s on a long session instead of 22 s - not-stop-ship, ruled by Darren Benson (operator) |
| BG1124 | Medium | critic.py brief's practice and claim-inventory refusals read the whole brief, so the unit diff US1094 embeds can satisfy them, and a unit whose own commit removes a practice gets its brief issued - not-stop-ship, ruled by Darren Benson (operator) |
| BG1125 | Medium | The review brief's unit diff is the whole run's diff over the unit's files, not the unit's own change, so on a shared file the 400-line cap is spent on other units' work and the unit's own hunks are cut - not-stop-ship, ruled by Darren Benson (operator) |
| BG1135 | Medium | critic.py supersede cannot retire either of two delivery rows that share a unit, date, reviewer and verdict - not-stop-ship, ruled by Darren Benson (operator) |
| CR0655 | Medium | Re-validate every open project lesson against the current tree, closing those no longer true - not-stop-ship, ruled by Darren Benson (operator) |
| BG1110 | Low | backlog_triage's duplicate lens has no way to record a pair confirmed distinct, so a triaged pair is re-reported on every run - not-stop-ship, ruled by Darren Benson (operator) |
| BG1115 | Low | A commit that adds a subcommand never selects test_cli_grammar.py, which reaches every script through surface.enumerate_scripts, so a grammar defect is first seen by the full suite at push - not-stop-ship, ruled by Darren Benson (operator) |
| BG1118 | Low | Six behaviours the self-check record, its brief gate and the author section state are pinned by no test (US1087, US1088, US1089 reviews) - not-stop-ship, ruled by Darren Benson (operator) |
| BG1119 | Low | Two behaviours BG1000's repair states for per-commit selection are pinned loosely or not at all: the census header's 40-line window, and the rewritten run reason - not-stop-ship, ruled by Darren Benson (operator) |
| BG1121 | Low | An author self-check record still reads stale in landing orders the per-file own-change view cannot see through: work recorded before its own commit, a cherry-pick, or another unit's hunk in a file the author also changed - not-stop-ship, ruled by Darren Benson (operator) |
| BG1123 | Low | A review brief now carries two different diffs of the unit: the scope line's `git diff <base> -- <Affects>` (the working tree) and US1094's UNIT DIFF section (base to HEAD) - not-stop-ship, ruled by Darren Benson (operator) |
| BG1126 | Low | A seat-requested amendment of an open run's goal leaves the run state on the old goal, so the close's goal read reports 'a different goal' - not-stop-ship, ruled by Darren Benson (operator) |
| BG1128 | Low | The close's goal panel and the next amendment's carry read only the latest goal-review round, while the plan reads every round on the latest wording, so after an owing seat records alone they disagree on which verdicts stand - not-stop-ship, ruled by Darren Benson (operator) |
| BG1129 | Low | test_lean_gate_host_docs.py's table test says a hook honouring a value other than 1 fails it, but an edit outside the lines `_hook_code` cuts passes it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1130 | Low | The builder brief's commit step quotes each Affects path with shlex.quote, but no test has a path with a space, so dropping the quoting stages the wrong paths with every test green - not-stop-ship, ruled by Darren Benson (operator) |
| BG1131 | Low | The close checklist's cost row never reads a run holding only its legacy baseline, and its main-thread-only re-derivation note has no test - not-stop-ship, ruled by Darren Benson (operator) |
| BG1132 | Low | BG0962's AC7 test proves only the REJECT half of 'the frozen verdict decides' when the per-unit ledger cannot be read - not-stop-ship, ruled by Darren Benson (operator) |
| BG1133 | Low | Three VELOCITY Priced/pt behaviours US1092 states are pinned by no test: the Source guard, an earlier row keeping its recorded figure, and rows with no Source named in the rate's basis - not-stop-ship, ruled by Darren Benson (operator) |
| BG1134 | Low | US1095's cost check is pinned only on the older retro shape, cost-baseline add reports a row the median never uses, and its latest-five window has no test - not-stop-ship, ruled by Darren Benson (operator) |
| CR0652 | Low | critic.py self-check record has no surface for a documentation unit's own prose, so the claims a doc unit makes in the file it changes cannot be recorded under that file - not-stop-ship, ruled by Darren Benson (operator) |
| CR0653 | Low | A delegated token total supplied for an agent outside this session is dropped whenever the session ran any subagent, because the reading's 'subagents included' flag is per session, not per agent - not-stop-ship, ruled by Darren Benson (operator) |
| CR0654 | Low | The builder brief tells the builder to write its story file and the self-check log, then commit only its Affects, without saying who commits those two - not-stop-ship, ruled by Darren Benson (operator) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-10-31T19:39:30Z | ebea81ff8c27f180 |

Signing records the principal, the date and this report's fingerprint against RUN-01M5EM9N.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 37,014,716 |

Total 37,014,716, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp; 2 reading(s) taken on an earlier counting basis were re-derived from the transcript, up to the moment each was taken, under the current one.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 12 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 40353565261/40344190434/40325755244/39814704911/39799503097/39783660435/39764286151/39741973489/39596925931/39591599543/39578192250/39562032268 - 12 push-triggered run(s) on main in the run window |
| Lead time for changes | 160h 25m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 77 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 40353565261/40344190434/40325755244/39814704911/39799503097/39783660435/39764286151/39741973489/39596925931/39591599543/39578192250/39562032268 - 12 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 40353565261/40344190434/40325755244/39814704911/39799503097/39783660435/39764286151/39741973489/39596925931/39591599543/39578192250/39562032268 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 7 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| neutrality | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| unit-tests | 2 | 2 | 0 | 2 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 1 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 1 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 5 | 15 |

### Not measured

Close checklist rows this run gave nothing to measure. Nothing is known to be wrong, so none is
a known issue; nothing is known to be right, so none reads as done.

| Row | State | Why |
| --- | --- | --- |
| cost: Cost, velocity and estimate accuracy | not measured | no per-unit telemetry, no measured run total and no supplied sprint total, so what this sprint cost is not attributable - which is not zero |
