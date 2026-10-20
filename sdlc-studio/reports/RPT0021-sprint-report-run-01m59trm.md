# Sprint Report: RUN-01M59TRM

## Goal

Rowan's push is judged on a configured gate host, and the gate's documents and weekly run tell the truth.

**Verdict: Judged partial** - Every clause of the goal holds on main, but two of the eleven units are carried, so the definition of done recorded at goal review (all eleven terminal, plus a live proof) is not met. Pushes are judged on devserver1 against exactly the commit pushed, proven live (US1075, US1077, US1078). The TRD and TSD were judged accurate (US1084, US1085, and US1086's documents). The weekly run reads true: dispatched run 39389634097 has corpus-verify at red-criteria 0, baseline 0 (BG1054, BG1099). US1076 (BG1078) and US1086 (BG1095) hit the review cap on test repairs that did not converge; their behaviour and documents are on main.

> **Run:** 2026-10-19T10:07:34Z to 2026-10-20T09:45:29Z (23.6h)
> **Verified on:** 6ceeae70fa961a03e1a9b82d7d08f14293413db0   **Fingerprint:** 69a1a2631ded6070

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 27 | 27 | 1.0x | 10 of 10 delivered unit(s) |
| Minutes | 145.9 | 5309.6 | 36.39x | measured active minutes (spans or agent minutes) against their forecast, over the 9 of 10 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 1417.9 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Tokens | 3,949,641 | 10,098,487 | NOT MEASURED - withheld - no delegated spend was supplied, so the actual is the main-thread meter alone, which cannot see a delegated agent's spend; each lane records its builder's total with `sprint lane return --tokens N` | the whole run: forecast over 10 of 10 unit(s) planned or added and not dropped; actual is the run meter, a lower bound |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| US1079 | 17.5 | 1407.9 | 438,849 | 10,098,487 |
| BG1066 | 17.5 | 1388.5 | 438,849 | 9,889,864 |
| US1075 | 29.2 | 1335.3 | 731,415 | 9,426,526 |
| US1077 | 11.7 | 47.2 | 292,566 | 551,611 |
| US1078 | 17.5 | 80.7 | 438,849 | 810,296 |
| BG1061 | 11.7 | 138.1 | 292,566 | 898,745 |
| US1084 | 17.5 | 88.5 | 438,849 | 651,739 |
| US1085 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1085 --delegated-minutes M` | 292,566 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1085 --delegated-minutes M` |
| BG1054 | 17.5 | 773.3 | 438,849 | 5,287,828 |
| BG1099 | 5.8 | 50.1 | 146,283 | 150,794 |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 11 | 31 |
| Delivered of the plan | 9 | 26 |
| Added mid-run and delivered | 1 of 1 added | 1 |
| Dropped | 2 | 5 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 27.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1079 | 3 | 3 | delivered | 2 |
| BG1066 | 3 | 3 | delivered | 2 |
| US1075 | 5 | 5 | delivered | 2 |
| US1076 | 3 | 3 | dropped - carried at the review cap: BG1078 | 2 |
| US1077 | 2 | 2 | delivered | 1 |
| US1078 | 3 | 3 | delivered | 2 |
| BG1061 | 2 | 2 | delivered | 2 |
| US1084 | 3 | 3 | delivered | 2 |
| US1085 | 2 | 2 | delivered | 2 |
| US1086 | 2 | 2 | dropped - carried at the review cap: BG1095 | 2 |
| BG1054 | 3 | 3 | delivered | 2 |
| BG1099 | 1 | 1 | added - BG1054's dispatched run found US1084's TSD rewording broke US0253 AC3; the operator chose to fix it this run; delivered | 1 |

## Known issues handed over

32 open finding(s) raised in the run, 2 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0650 | High | The author's self-check is a step the tools run and require, not a rule an agent remembers - not-stop-ship, ruled by Darren Benson (operator) |
| BG1078 | Medium | US1076 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by Darren Benson (operator) |
| BG1087 | Medium | mutation.py's changed-line scope finds no lines on a machine whose git config sets diff.mnemonicprefix or diff.noprefix - not-stop-ship, ruled by Darren Benson (operator) |
| BG1095 | Medium | US1086 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by Darren Benson (operator) |
| BG1101 | Medium | test_repo_hygiene writes probe fixtures into the real scripts/tests directory, so a parallel test copying that tree can fail - not-stop-ship, ruled by Darren Benson (operator) |
| BG1070 | Low | conformance reads US0357 and US0358 as missing their verified stage in a fresh checkout, though both carry Verified stamps, so the lane's verdict depends on the clone's .local state - not-stop-ship, ruled by Darren Benson (operator) |
| BG1071 | Low | The project seat card's design-persona check stops at a full stop, so a name followed by a file path before 'design persona' passes - not-stop-ship, ruled by Darren Benson (operator) |
| BG1072 | Low | test_persona_coherence's id check reads a fixed list of id prefixes, so a card citing a handoff or test-spec id that resolves to nothing passes - not-stop-ship, ruled by Darren Benson (operator) |
| BG1073 | Low | critic.py record writes a reviewer's findings verbatim into a ledger the repository's markdownlint refuses, so a finding quoting an email-shaped name blocks the next commit - not-stop-ship, ruled by Darren Benson (operator) |
| BG1074 | Low | No test pins that a red gate-host run records its duration, so the hook can stop recording exit 1 with the suite green - not-stop-ship, ruled by Darren Benson (operator) |
| BG1075 | Low | tools/remote-gate.sh's local side needs bash 4, so a pusher on stock macOS bash 3.2 has every gate-host push refused - not-stop-ship, ruled by Darren Benson (operator) |
| BG1076 | Low | The rejoinder brief asks a reviewer to rule each earlier finding, but the return contract has no place for the rulings, so a round-2 verdict that writes them untagged is refused by critic.py record - not-stop-ship, ruled by Darren Benson (operator) |
| BG1079 | Low | A unit carried at the review cap gets a criterion for every ISSUES item, including info rulings and pre-existing findings already filed - not-stop-ship, ruled by Darren Benson (operator) |
| BG1080 | Low | remote-gate doctor calls a host ready without checking flock and setsid, which every push run on it needs - not-stop-ship, ruled by Darren Benson (operator) |
| BG1081 | Low | remote-gate doctor sources gate-env.sh from its temporary directory, where the gate sources it from the host's home - not-stop-ship, ruled by Darren Benson (operator) |
| BG1082 | Low | Four of remote-gate doctor's stated behaviours have no test that fails without them - not-stop-ship, ruled by Darren Benson (operator) |
| BG1083 | Low | enable-hooks.sh's tolerance of an unready or unreachable gate host has no test - not-stop-ship, ruled by Darren Benson (operator) |
| BG1084 | Low | remote-gate doctor's exit codes are documented as 0, 1 and 3, and a missing transport is reported as an unready host - not-stop-ship, ruled by Darren Benson (operator) |
| BG1085 | Low | remote-gate doctor prints the local clone's Python install route for a gap on the gate host - not-stop-ship, ruled by Darren Benson (operator) |
| BG1086 | Low | run-suite.sh's passed count needs bc, which is not a declared prerequisite, and is null with a broken-pipe error where bc is absent - not-stop-ship, ruled by Darren Benson (operator) |
| BG1088 | Low | A setup fault on a gate host's suite run is named as 'did not run the all suite' with no test that fails without it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1089 | Low | US1078 AC3's Verify test does not exercise the verdict's binding to the tree sent; only a sibling test does - not-stop-ship, ruled by Darren Benson (operator) |
| BG1090 | Low | test_output_prints_in_declared_order_whatever_finishes_first failed one subtest under heavy load, and passes alone; not yet diagnosed - not-stop-ship, ruled by Darren Benson (operator) |
| BG1091 | Low | US1084's document tests still pass three phrasings they exist to refuse - not-stop-ship, ruled by Darren Benson (operator) |
| BG1092 | Low | The TSD says the commit-msg hook falls back to skill-tests.sh only without pytest; it also does when the handover carries no selectors - not-stop-ship, ruled by Darren Benson (operator) |
| BG1093 | Low | BG1061's heading checks read a heading's trailing space as its last character, so a mark left behind a space passes - not-stop-ship, ruled by Darren Benson (operator) |
| BG1094 | Low | A lesson that is only punctuation gets an empty heading title since BG1061 - not-stop-ship, ruled by Darren Benson (operator) |
| BG1096 | Low | The TRD says verify_ac run --coverage refuses under block and reports under report when coverage is absent; the split is the Done gate's - not-stop-ship, ruled by Darren Benson (operator) |
| BG1097 | Low | US1085's toolchain-doc tests leave coverage unpinned, still pass three counted phrasings, and fail at collection without PyYAML - not-stop-ship, ruled by Darren Benson (operator) |
| BG1098 | Low | AGENTS.md gives the local boundary-push series as the push's cost on a clone that names a gate host - not-stop-ship, ruled by Darren Benson (operator) |
| BG1100 | Low | gate.py's verify ceiling still calls 300 s CI's figure, though corpus-verify now runs every criterion under 450 s - not-stop-ship, ruled by Darren Benson (operator) |
| BG1102 | Low | The corpus-verify timing step's ceiling is pinned only as an integer, so one as long as the job's own cap passes - not-stop-ship, ruled by Darren Benson (operator) |
| lessons-summary | close gap | refused: LESSONS-SUMMARY.md lists 441 lesson(s) the log at /home/darren/code/DarrenBenson/sdlc-studio/sdlc-studio/retros/LESSONS.md does not hold (L-0442: Run each user-facing sentence in a changelog fragment through the CLI before asking for review, as the paperwork reviews already do, L-0441: Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped…, L-0440: A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_` scrub broke… (+438 more)), so this log is not the one the summary was built from. Restore the log from the machine that ran the last close, or merge it, and run this again. Nothing was written. |
| gate | close gap | lessons-summary: LESSONS-SUMMARY.md is STALE - 2 lesson(s) added since it was regenerated: L-0002: Write a documentation unit's criteria against structured content a test can compare exactly, such as a table cell's set read from the…, L-0001: Before every brief, mutate my own tests as the QA seat does, with paraphrases, swapped clauses and a negation elsewhere in the sentence…; 441 closed or removed since: L-0442: Run each user-facing sentence in a changelog fragment through the CLI before asking for review, as the paperwork reviews already do, L-0441: Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped…, L-0440: A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_` scrub broke… (+438 more). Regenerate it: scripts/lessons.py summary |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-10-20T15:38:05Z | 69a1a2631ded6070 |

Signing records the principal, the date and this report's fingerprint against RUN-01M59TRM.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 10,098,487 |

Total 10,098,487, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 18 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 39392921925/39389633678/39322204508/39317590448/39315716391/39312220156/39307080528/39302574041/39294371349/39288005794/39283565141/39279699470/39255842339/39248977496/39243631708/39241288465/39239542114/39237451586 - 18 push-triggered run(s) on main in the run window |
| Lead time for changes | 22h 43m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 37 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 39392921925/39389633678/39322204508/39317590448/39315716391/39312220156/39307080528/39302574041/39294371349/39288005794/39283565141/39279699470/39255842339/39248977496/39243631708/39241288465/39239542114/39237451586 - 18 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 39392921925/39389633678/39322204508/39317590448/39315716391/39312220156/39307080528/39302574041/39294371349/39288005794/39283565141/39279699470/39255842339/39248977496/39243631708/39241288465/39239542114/39237451586 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 146,283 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

3 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| markdown | 1 | 0 | 1 | too few runs: 2 of 3 recorded |
| message-refs | 2 | 0 | 2 | too few runs: 2 of 3 recorded |
| repo-writes | 0 | 0 | 0 | too few runs: 2 of 3 recorded |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | graduating (CR0642) | 0 | 2 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 0 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 6 | 10 |
