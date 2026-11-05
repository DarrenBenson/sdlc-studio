# Sprint Report: RUN-01M6F74P

## Goal

`gate.py --release` passes first time at default ceilings in about one suite run; band drift and commit frictions fixed.

**Verdict: Judged partial** - The release verify lane ran at default ceilings in 1,272 s on the gate host (6.2.0's took 4,447 to 6,582 s) and band drift and the commit frictions are fixed, but the one release gate on the closing commit did not pass first time: three criteria need Python 3.10 and pdftotext, which the gate host lacks (BG1220), one red came from a filed bug's own text, and the fragments lane refuses any commit before a cut.

> **Run:** 2026-11-02T22:49:45Z to 2026-11-04T20:35:24Z (45.8h)
> **Verified on:** 3207e8703e3c81bb5e85bfd4196525ce65a66435   **Fingerprint:** dd48acac19cd992b

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 54 | 57 | 1.06x | 23 of 23 delivered unit(s) |
| Minutes | 297.7 | 1832.0 | 6.15x | measured active minutes (spans or agent minutes) against their forecast, over the 20 of 23 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 2745.7 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 144,830,680 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 44,019,404 (input 7,676 x1, output 2,096,736 x5, cache write 5m 41,067,170 x1.25, cache write 1h 847,822 x2, cache read 813,097,176 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 10,057,608 | 44,019,404 | 4.38x | the whole run: forecast over 23 of 23 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 20 delegated total(s) supplied are not added |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0958 | 5.8 | 26.0 agent minutes | 186,252 | 83,830 agent tokens |
| BG1090 | 5.8 | 26.0 agent minutes | 186,252 | 83,830 agent tokens |
| BG1114 | 11.7 | 101.0 agent minutes | 372,504 | 120,941 agent tokens |
| BG1116 | 5.8 | 35.0 agent minutes | 186,252 | 111,044 agent tokens |
| BG1122 | 17.5 | 70.0 agent minutes | 558,756 | 228,245 agent tokens |
| BG1147 | 11.7 | 26.0 agent minutes | 372,504 | 91,977 agent tokens |
| BG1160 | 11.7 | 101.0 agent minutes | 372,504 | 120,941 agent tokens |
| BG1163 | 29.2 | 75.0 agent minutes | 931,260 | 243,379 agent tokens |
| BG1167 | 29.2 | 108.0 agent minutes | 931,260 | 392,430 agent tokens |
| US1112 | 17.5 | 308.0 agent minutes | 558,756 | 673,741 agent tokens |
| US1113 | 17.5 | 198.0 agent minutes | 558,756 | 538,957 agent tokens |
| US1114 | 17.5 | 41.0 agent minutes | 558,756 | 284,697 agent tokens |
| US1115 | 11.7 | 38.0 agent minutes | 372,504 | 134,418 agent tokens |
| US1116 | 5.8 | 18.0 agent minutes | 186,252 | 67,209 agent tokens |
| BG1183 | 11.7 | 380.0 agent minutes | 372,504 | 885,575 agent tokens |
| BG1187 | 11.7 | 83.0 agent minutes | 372,504 | 196,516 agent tokens |
| US0989 | 29.2 | 48.0 agent minutes | 931,260 | 195,820 agent tokens |
| US0990 | 17.5 | 45.0 agent minutes | 558,756 | 238,716 agent tokens |
| US0991 | 17.5 | 57.0 agent minutes | 558,756 | 261,486 agent tokens |
| BG1197 | 11.7 | 48.0 agent minutes | 372,504 | 165,230 agent tokens |
| BG1210 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1210 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1210 --delegated-minutes M` |
| BG1212 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1212 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1212 --delegated-minutes M` |
| BG1216 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1216 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1216 --delegated-minutes M` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 15 | 36 |
| Delivered of the plan | 15 | 36 |
| Added mid-run and delivered | 8 of 9 added | 18 |
| Dropped | 1 | 5 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 57.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0958 | 1 | 1 | delivered | 1 |
| BG1090 | 1 | 1 | delivered | 1 |
| BG1114 | 2 | 2 | delivered | 1 |
| BG1116 | 1 | 1 | delivered | 2 |
| BG1122 | 3 | 3 | delivered | 1 |
| BG1147 | 2 | 2 | delivered | 1 |
| BG1160 | 2 | 2 | delivered | 1 |
| BG1163 | 5 | 5 | delivered | 2 |
| BG1167 | 5 | 5 | delivered | 2 |
| US1112 | 3 | 3 | delivered | 2 |
| US1113 | 3 | 3 | delivered | 2 |
| US1114 | 3 | 3 | delivered | 1 |
| US1115 | 2 | 2 | delivered | 1 |
| US1116 | 1 | 1 | delivered | 1 |
| BG1183 | 2 | 5 | delivered | 2 |
| BG1187 | 2 | 2 | added - no reason recorded; delivered | 1 |
| US0986 | 5 | 5 | dropped - carried at the review cap: BG1205 | 2 |
| US0989 | 5 | 5 | added - no reason recorded; delivered | 1 |
| US0990 | 3 | 3 | added - no reason recorded; delivered | 2 |
| US0991 | 3 | 3 | added - no reason recorded; delivered | 1 |
| BG1197 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1210 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1212 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1216 | 1 | 1 | added - no reason recorded; delivered | 1 |

## Known issues handed over

34 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0661 | High | A sprint costs 3.75M priced tokens per point in run five against run four's 1.61M and a norm near 1M, and its per-unit ceremony is the largest share - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| CR0662 | High | Measure a Cursor CLI run's tokens from the afterAgentResponse hook or a captured print-mode result, since the CLI's store keeps no usage - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1190 | Medium | A verifier that times out is killed alone, so its children run on and load every verifier after it - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1205 | Medium | US0986 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1213 | Medium | The Cursor usage reader accepts an http:// SDLC_STUDIO_CURSOR_API base, so an override would send the bearer key in cleartext - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1217 | Medium | gate.py --run-tests still reads green when a selector names a test that does not exist in a file that does, beside a failing module, under xdist - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1220 | Medium | The gate host lacks Python 3.10 and pdftotext, so the release route reads three passing criteria red - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1185 | Low | BG1167's rule reads a light APPROVE's scope from git history, so three narrow orderings still count a unit whose own Affects widened as covered - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1186 | Low | The release verify lane's declared budget is 600 s against a measured 3,340 s, so every release run prints OVER and the pin keeps it there - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1188 | Low | One lane-cap test took 695 s on a worker, re-running its whole class once per hook lane - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1189 | Low | reference-verify.md#batch says only jest batches, but verify_ac has a pytest batch cache that the release lane uses - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1191 | Low | The batch's phase plugin reads serial_only before a conftest's own trylast hook, so a mark that hook applies runs on an xdist worker - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1192 | Low | US1113 AC3's one-at-a-time pin lets a concurrent serial pool through under load, because its three 0.5 s probes must start within 0.5 s of each other - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1193 | Low | sdlc_md.corpus_cache hands later callers the path spelling of the first walk, so a relative root then an absolute one raises ValueError in reconcile - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1194 | Low | remote-gate.sh's release route does not send SDLC_GATE_BOUNDARY, so a value set in the shell changes the local release gate but not the host's - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1195 | Low | Four test modules of tools/remote-gate.sh name no test-census-subject, so a commit to the script runs only one of the five - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1196 | Low | No test pins the host's SDLC_STUDIO_BOUNDARY_SUITE=1 export for remote-gate.sh's push and suite jobs - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1198 | Low | reference-config.md says the commit-msg hook refuses a commit without a Refs: trailer per owning id, and does not name the Mentions: trailer US1115 added - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1199 | Low | US1115's reference and fragment say a commit whose every id is a mention is attributed no files, but a one-id subject whose only id is a Mentions: id is attributed its files - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1200 | Low | mutation.changed_lines reports no lines when git's color.ui or color.diff is always, because the +++ b/ header arrives wrapped in ANSI codes - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1201 | Low | US0989's Cursor usage reader takes its variable names and response shape from documentation, not from a real Cursor cloud run - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1202 | Low | US0989's Cursor reader leaves two guards unpinned and names an empty usage for a malformed answer - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1203 | Low | US0991 AC3's Verify line cannot fail on the close's main-thread prose, which only a sibling test pins - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1204 | Low | A run metered by two harnesses adds the supplied delegated totals in full, even over a reading that already holds delegated spend - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1206 | Low | BG1116's pins key on literal wording: the boundary-habit test refuses only gate.py, and the per-commit and AGENTS.md checks pass reworded regressions - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1207 | Low | BG1197's harness scrub lives in the root conftest, so unittest runs (skill-tests.sh, the hook's unittest fallback) still read the harness from the environment - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1208 | Low | BG1122's meter memo leaves the unfinished-line size refresh unpinned, and its changelog's equals-a-whole-read claim holds only for append-only growth - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1209 | Low | The pre-commit hook's payload markdown lane quotes its markdownlint path untested, because the BG1147 fixture tracks no markdown under .claude/ - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1211 | Low | The shell-hazard check flags unittest's own assertion separator (the spaced colon after an assertion's operands) when a reviewer's finding quoting it is carried into a bug - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1214 | Low | BG1212's AC2 docstring says only a clock can see the no-timeout join mutant, but the clock-free AC2 test also fails on it - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1215 | Low | verify_ac's fallback for a queued collection that raised is untested, so dropping it would read a live stamp as stale - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1218 | Low | A critic brief spends most of its 5 to 13 s in the per-unit affect-key parse, and a refused brief still renders before the self-check gate - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1219 | Low | migrate's dry run leaves its private bytecode directory behind when verify_ac's ceiling kills it, and BG1183 AC1 cannot pass verify_ac at its 120 s default - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0404) |
| BG1222 | Low | The hand-copied-list census runs only at the push gate and matches any three quoted .py names, fixture names included |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 1 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-05T07:03:35Z | dd48acac19cd992b |

Signing records the principal, the date and this report's fingerprint against RUN-01M6F74P.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 44,019,404 |

Total 44,019,404, of which delegated 5,118,982. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 41911840410/41627174372 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 45h 56m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 63 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 41911840410/41627174372 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 41911840410/41627174372 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 3 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

12 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 3 | 0 | 3 | delete candidate: 6 refusal(s) over 3 runs and no candidate catch |
| markdown | 3 | 0 | 3 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| message-refs | 5 | 0 | 5 | delete candidate: 5 refusal(s) over 3 runs and no candidate catch |
| neutrality | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| style | 1 | 1 | 0 | 1 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | 2 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 1 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 1 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 3 | 24 |
