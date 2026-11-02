# Sprint Report: RUN-01M6A3K2

## Goal

6.2 is releasable: its documents and personas match the code, every lesson is judged, and gates cost less.

**Verdict: Judged partial** - Every lesson is judged and the commit gate fell from 38.6s to 14.6s, but the push gate stayed at about 610s and filed false sentences remain in the TRD, TSD and a persona card (D0394)

> **Run:** 2026-10-31T23:12:36Z to 2026-11-02T07:15:32Z (32.0h)
> **Verified on:** 72cf1aead22d33ec8ceb9e2e5c562c1e145e03ca   **Fingerprint:** 795b535a9b3bcd7a

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 69 | 69 | 1.0x | 24 of 24 delivered unit(s) |
| Minutes | 402.6 | NOT MEASURED - no unit carries a measured time (an In Progress span or agent minutes) | NOT MEASURED - needs both a forecast and an actual | the whole run: forecast over 24 of 24 unit(s) planned or added and not dropped; no unit carries both a forecast and a measured time |
| Wall-clock span | not forecast | 1922.9 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 111,425,278 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 23,269,314 (input 8,914 x1, output 1,251,402 x5, cache write 5m 20,807,150 x1.25, cache write 1h 1,201,848 x2, cache read 767,467,209 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 12,851,388 | 23,269,314 | 1.81x | the whole run: forecast over 24 of 24 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0963 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0963 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0963 --delegated-minutes M` |
| BG1065 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1065 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1065 --delegated-minutes M` |
| BG1109 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1109 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1109 --delegated-minutes M` |
| BG1135 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1135 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1135 --delegated-minutes M` |
| BG1139 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1139 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1139 --delegated-minutes M` |
| US1080 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1080 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1080 --delegated-minutes M` |
| US1081 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1081 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1081 --delegated-minutes M` |
| US1082 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1082 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1082 --delegated-minutes M` |
| US1083 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1083 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1083 --delegated-minutes M` |
| US1098 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1098 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1098 --delegated-minutes M` |
| US1099 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1099 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1099 --delegated-minutes M` |
| US1100 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1100 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1100 --delegated-minutes M` |
| US1101 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1101 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1101 --delegated-minutes M` |
| US1103 | 29.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1103 --delegated-minutes M` | 931,260 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1103 --delegated-minutes M` |
| US1104 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1104 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1104 --delegated-minutes M` |
| US1102 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1102 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1102 --delegated-minutes M` |
| US1105 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1105 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1105 --delegated-minutes M` |
| US1106 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1106 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1106 --delegated-minutes M` |
| US1107 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1107 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1107 --delegated-minutes M` |
| US1108 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1108 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1108 --delegated-minutes M` |
| US1109 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1109 --delegated-minutes M` | 558,756 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1109 --delegated-minutes M` |
| BG1137 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1137 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1137 --delegated-minutes M` |
| BG1138 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1138 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1138 --delegated-minutes M` |
| BG1140 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1140 --delegated-minutes M` | 372,504 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1140 --delegated-minutes M` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 24 | 69 |
| Delivered of the plan | 24 | 69 |
| Added mid-run and delivered | 0 of 0 added | 0 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 69.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0963 | 5 | 5 | delivered | 2 |
| BG1065 | 1 | 1 | delivered | 2 |
| BG1109 | 5 | 5 | delivered | 1 |
| BG1135 | 2 | 2 | delivered | 1 |
| BG1139 | 3 | 3 | delivered | 1 |
| US1080 | 3 | 3 | delivered | 1 |
| US1081 | 2 | 2 | delivered | 2 |
| US1082 | 1 | 1 | delivered | 2 |
| US1083 | 1 | 1 | delivered | 1 |
| US1098 | 3 | 3 | delivered | 2 |
| US1099 | 3 | 3 | delivered | 2 |
| US1100 | 5 | 5 | delivered | 1 |
| US1101 | 5 | 5 | delivered | 1 |
| US1103 | 5 | 5 | delivered | 2 |
| US1104 | 3 | 3 | delivered | 1 |
| US1102 | 3 | 3 | delivered | 2 |
| US1105 | 3 | 3 | delivered | 1 |
| US1106 | 3 | 3 | delivered | 2 |
| US1107 | 3 | 3 | delivered | 2 |
| US1108 | 3 | 3 | delivered | 2 |
| US1109 | 3 | 3 | delivered | 2 |
| BG1137 | 1 | 1 | delivered | 1 |
| BG1138 | 1 | 1 | delivered | 1 |
| BG1140 | 2 | 2 | delivered | 1 |

## Known issues handed over

31 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1147 | Medium | The pre-commit markdown lane skips in a linked worktree, because it looks for markdownlint only in that worktree's node_modules - not-stop-ship, ruled by Darren Benson (operator) |
| BG1160 | Medium | gate.py --run-tests prints 'no tests ran' and exits 0 when one of its modules is missing, even if a real module beside it fails - not-stop-ship, ruled by Darren Benson (operator) |
| BG1163 | Medium | The TRD's lifecycle table states a tracked record is filed on every close, which --file-and-close does not do, and the .local writer pin accepts an orphaned writer - not-stop-ship, ruled by Darren Benson (operator) |
| BG1167 | Medium | Conformance re-derives a closed unit's risk band from today's tree, so a later unit's edit to a shared file fails a light APPROVE that was right when given, and the census names the wrong remedy - not-stop-ship, ruled by Darren Benson (operator) |
| CR0656 | Medium | A command to amend a planned unit's Affects or a criterion in flight, recording why, so a builder's scope finding is not a hand edit - not-stop-ship, ruled by Darren Benson (operator) |
| CR0657 | Medium | Lesson Revalidated reasons cite file:line evidence that drifts as code lands; check and re-anchor it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1142 | Low | doc-freshness is described as a LATEST.md check everywhere, though it now censuses the TRD, PRD and TSD; one hook comment lists it as a per-commit lane - not-stop-ship, ruled by Darren Benson (operator) |
| BG1143 | Low | doc_freshness's baseline leg has no pin for checking every Coverage line, nor for skipping the revision history - not-stop-ship, ruled by Darren Benson (operator) |
| BG1144 | Low | The commit hook's unittest fallback ignores pytest's serial_only and boundary_only marks, so a push-only test still runs on a commit there - not-stop-ship, ruled by Darren Benson (operator) |
| BG1145 | Low | readiness's carry note names a re-review that critic.py record refuses for a unit at the cap with no filed carry bug; only a --ruling discharges it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1146 | Low | lessons.py revalidate --close appends its Status bullet straight after a paragraph, so the lessons log fails markdownlint MD032 - not-stop-ship, ruled by Darren Benson (operator) |
| BG1148 | Low | revalidate's real-date guard has no test, its refusal prefix names --extend for any bad fields file, and the gate hint and four docs show --extend with no --reason - not-stop-ship, ruled by Darren Benson (operator) |
| BG1149 | Low | RFC0048's resolved D6 still states a 120s per-commit gate budget against a 99s baseline, while the config has declared 480s against 400s since 2026-09-20 - not-stop-ship, ruled by Darren Benson (operator) |
| BG1150 | Low | sprint.py still says the planner reads the series 'the budget lane reads', though that lane was deleted in 315ec358 - not-stop-ship, ruled by Darren Benson (operator) |
| BG1151 | Low | The interface-path persona router reads a template placeholder as a declared interface, cuts a row at an escaped pipe, leaves ./ unpinned, and disagrees with validate on overlap - not-stop-ship, ruled by Darren Benson (operator) |
| BG1152 | Low | artifact.py batch writes a list-valued affects as a Python repr, so the Affects line reads ['hooks/pre-push'] - not-stop-ship, ruled by Darren Benson (operator) |
| BG1153 | Low | EXECUTES_VERIFIERS's docstring says verify_ac reads it, but verify_ac keeps its own VERIFIABLE_PREFIXES, and the TRD says an un-decomposed CR 'reaches Done' - not-stop-ship, ruled by Darren Benson (operator) |
| BG1154 | Low | Trevor's card says a sign-off on each unit is declined, though sprint.py sign writes a per-unit sign-off row under the one signature - not-stop-ship, ruled by Darren Benson (operator) |
| BG1155 | Low | decisions.read_once's change detection is pinned only by a growing file: dropping inode, mtime or ctime from its identity stays green - not-stop-ship, ruled by Darren Benson (operator) |
| BG1156 | Low | test_persona_coherence's span recogniser skips some `script.py verb` shapes, and its mixed-unit probe cannot tell first-listed Primary from first-path owner - not-stop-ship, ruled by Darren Benson (operator) |
| BG1157 | Low | No test pins that a --host prerequisite check still names a missing markdownlint, so widening PUSHER_ONLY to it stays green - not-stop-ship, ruled by Darren Benson (operator) |
| BG1158 | Low | The TRD verifier-authority scan misses some story-only rewordings and fails true sentences about a story-only run - not-stop-ship, ruled by Darren Benson (operator) |
| BG1159 | Low | supersede's reference omits --brief and row-brief, two of its new guarantees are unpinned, and a no-match refusal contradicts itself - not-stop-ship, ruled by Darren Benson (operator) |
| BG1161 | Low | A clean-checkout gate.py run judges conformance over the whole workspace and reads OVER the standard budget every time - not-stop-ship, ruled by Darren Benson (operator) |
| BG1162 | Low | PrdRulesTests' protections are thinner than its claims: four PRD facts can drift past it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1164 | Low | ADR-009 omits the generic persona rung, the TRD gh-caller scan reads only a literal argv, and sprint's fetch-failure reason is garbled - not-stop-ship, ruled by Darren Benson (operator) |
| BG1165 | Low | The TSD's Security Testing section says the script contract forbids network calls except the gh wrapper, but a version-check GET and git fetch origin also call out - not-stop-ship, ruled by Darren Benson (operator) |
| BG1168 | Low | The PRD test's unreleased-marker check strips code spans from the whole row, and PRD edits land with no Revision History row - not-stop-ship, ruled by Darren Benson (operator) |
| BG1169 | Low | mutation.py's _drop_ignored ignores git check-ignore's exit code, so one path git refuses leaves the rest partly filtered - not-stop-ship, ruled by Darren Benson (operator) |
| BG1170 | Low | The TSD and TRD refresh tests leave low residual gaps their round-2 and BG1166 reviews named - not-stop-ship, ruled by Darren Benson (operator) |
| BG1171 | Low | reconcile settle closes an epic in the pre-commit hook but leaves the requests that close made derivable, so the same commit's gate refuses on that drift - not-stop-ship, ruled by Darren Benson (operator) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-02T07:17:43Z | 795b535a9b3bcd7a |

Signing records the principal, the date and this report's fingerprint against RUN-01M6A3K2.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 23,269,314 |

Total 23,269,314, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 4 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 41293856806/41277013912/41272443826/41261170080 - 4 push-triggered run(s) on main in the run window |
| Lead time for changes | 20h 29m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 84 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 41293856806/41277013912/41272443826/41261170080 - 4 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 41293856806/41277013912/41272443826/41261170080 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 1 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

3 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 2 | 0 | 2 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| neutrality | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| unit-tests | 0 | 0 | 0 | 2 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 6 | 21 |
