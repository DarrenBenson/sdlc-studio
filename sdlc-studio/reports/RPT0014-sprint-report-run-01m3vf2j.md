# Sprint Report: RUN-01M3VF2J

## Goal

Every open finding closes: Maya and Jonah get honest commands, safe installs and upgrades, and leaner sprint machinery

**Verdict: Judged achieved** - Every unit the plan held closed: 40 of 40 approved by an independent QA seat (34 in the batch, 6 discharged by their rejecting reviewers after a carry at the cap), 34 of 34 batch units verify green. Honest commands: a CLI no longer reports success it did not get (US0969), ids print as their files spell them (BG0825, BG0877), docs and comments tell the truth (US0973). Safe installs and upgrades: install.sh takes the latest verified release (US0968), install and upgrade never damage a consumer's files (US0976), a v5 upgrade reads clean and names an unreadable file (US0974), migrate names retired surface in a project's own docs (US0975), js-yaml, brace-expansion and markdown-it held at patched releases (BG0866, BG0876). Leaner machinery: the handoff page, its writers and --require-handoff are retired for the signed report (US0967, US0978), the revert-check lane and batch-span API are gone (US0784, BG0861). Disclosed: 20 findings raised during the run (BG0870-BG0889, all groomed) stay open for the next sprint.

> **Run:** 2026-10-01T10:19:17Z to open (9.6h)
> **Verified on:** 8d083c6848d5ab661d3bbbf8b2bf00634476b0bd   **Fingerprint:** 8cb2f1bb218180d9

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 65 | 65 | 1.0x | 34 of 34 delivered unit(s) |
| Minutes | 416.0 | 575.6 | 1.38x | the whole run: forecast over 34 of 34 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 11,467,105 | 2,350,747 | 0.2x | the whole run: forecast over 34 of 34 unit(s) planned or added and not dropped; actual is the run meter, a lower bound |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. Spans of
units open at the same time overlap, so no per-unit figure is added up into the run's figures
above.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0726 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0726 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0726 --delegated-minutes M` |
| BG0737 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0737 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0737 --delegated-minutes M` |
| BG0817 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0817 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0817 --delegated-minutes M` |
| BG0827 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0827 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0827 --delegated-minutes M` |
| BG0832 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0832 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0832 --delegated-minutes M` |
| BG0833 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0833 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0833 --delegated-minutes M` |
| BG0834 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0834 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0834 --delegated-minutes M` |
| BG0835 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0835 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0835 --delegated-minutes M` |
| BG0866 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0866 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0866 --delegated-minutes M` |
| US0804 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0804 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0804 --delegated-minutes M` |
| US0966 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0966 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0966 --delegated-minutes M` |
| BG0867 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0867 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0867 --delegated-minutes M` |
| BG0868 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0868 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0868 --delegated-minutes M` |
| BG0869 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0869 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0869 --delegated-minutes M` |
| BG0855 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0855 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0855 --delegated-minutes M` |
| BG0860 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0860 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0860 --delegated-minutes M` |
| US0759 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0759 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0759 --delegated-minutes M` |
| US0784 | 12.8 | 492.2 | 352,834 | 2,201,056 |
| US0968 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0968 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0968 --delegated-minutes M` |
| US0973 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0973 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0973 --delegated-minutes M` |
| BG0825 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0825 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0825 --delegated-minutes M` |
| BG0831 | 19.2 | 474.7 | 529,251 | 2,158,892 |
| BG0837 | 19.2 | 546.1 | 529,251 | 2,281,764 |
| BG0861 | 19.2 | 524.0 | 529,251 | 2,261,843 |
| US0805 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0805 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0805 --delegated-minutes M` |
| US0969 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0969 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0969 --delegated-minutes M` |
| US0970 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0970 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0970 --delegated-minutes M` |
| US0972 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0972 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0972 --delegated-minutes M` |
| BG0858 | 12.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0858 --delegated-minutes M` | 352,834 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0858 --delegated-minutes M` |
| US0975 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0975 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0975 --delegated-minutes M` |
| US0976 | 19.2 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0976 --delegated-minutes M` | 529,251 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US0976 --delegated-minutes M` |
| US0967 | 32.0 | 436.4 | 882,085 | 2,088,606 |
| BG0876 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0876 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0876 --delegated-minutes M` |
| BG0877 | 6.4 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0877 --delegated-minutes M` | 176,417 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0877 --delegated-minutes M` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 38 | 78 |
| Delivered of the plan | 32 | 63 |
| Added mid-run and delivered | 2 of 2 added | 2 |
| Dropped | 6 | 15 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 65.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0726 | 1 | 1 | delivered | 1 |
| BG0737 | 1 | 1 | delivered | 1 |
| BG0817 | 1 | 1 | delivered | 1 |
| BG0827 | 1 | 1 | delivered | 1 |
| BG0832 | 1 | 1 | delivered | 1 |
| BG0833 | 1 | 1 | delivered | 1 |
| BG0834 | 1 | 1 | delivered | 1 |
| BG0835 | 1 | 1 | delivered | 1 |
| BG0866 | 1 | 1 | delivered | 1 |
| US0804 | 1 | 1 | delivered | 1 |
| US0966 | 1 | 1 | delivered | 2 |
| BG0867 | 1 | 1 | delivered | 2 |
| BG0868 | 1 | 1 | delivered | 1 |
| BG0869 | 1 | 1 | delivered | 1 |
| BG0824 | 2 | 2 | dropped - carried at the review cap: BG0883 | 3 |
| BG0839 | 2 | 2 | dropped - carried at the review cap: BG0880 | 3 |
| BG0855 | 2 | 2 | delivered | 1 |
| BG0860 | 2 | 2 | delivered | 2 |
| US0759 | 2 | 2 | delivered | 2 |
| US0784 | 2 | 2 | delivered | 1 |
| US0968 | 2 | 2 | delivered | 1 |
| US0973 | 2 | 2 | delivered | 2 |
| US0977 | 2 | 2 | dropped - carried at the review cap: BG0879 | 3 |
| BG0825 | 3 | 3 | delivered | 1 |
| BG0831 | 3 | 3 | delivered | 2 |
| BG0837 | 3 | 3 | delivered | 1 |
| BG0861 | 3 | 3 | delivered | 1 |
| US0805 | 3 | 3 | delivered | 1 |
| US0969 | 3 | 3 | delivered | 1 |
| US0970 | 3 | 3 | delivered | 2 |
| US0971 | 3 | 3 | dropped - carried at the review cap: BG0884 | 3 |
| US0972 | 3 | 3 | delivered | 2 |
| US0974 | 3 | 3 | dropped - carried at the review cap: BG0875 | 3 |
| BG0858 | 2 | 2 | delivered | 1 |
| US0975 | 3 | 3 | delivered | 2 |
| US0976 | 3 | 3 | delivered | 2 |
| US0967 | 5 | 5 | delivered | 2 |
| US0978 | 3 | 3 | dropped - carried at the review cap: BG0874 | 3 |
| BG0876 | 1 | 1 | added - found by this run's QA review of BG0866/BG0825; same files as a lane already in the batch (D0290: inside the repo and the approved batch's scope); delivered | 1 |
| BG0877 | 1 | 1 | added - found by this run's QA review of BG0866/BG0825; same files as a lane already in the batch (D0290: inside the repo and the approved batch's scope); delivered | 1 |

## Known issues handed over

11 open finding(s) raised in the run, 2 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0870 | Medium | The pre-push hook's fail-closed checkout and annotated-tag peel are unpinned, it runs the release lanes on a branch tip pushed beside a tag, and an interrupted push leaves a prunable worktree - not-stop-ship, ruled by Claude (orchestrator) |
| BG0871 | Medium | The diff-scoped gate lanes judge nothing at the push boundary, because their scope is the working-tree diff, which is empty on a clean pushed commit - not-stop-ship, ruled by Claude (orchestrator) |
| BG0872 | Medium | next_id.py allocate mints a sequential id on a schema v3 project, where artifact.py new mints a ULID - not-stop-ship, ruled by Claude (orchestrator) |
| BG0873 | Low | reconcile reports a v3-keyed handoff file as an orphan index row - not-stop-ship, ruled by Claude (orchestrator) |
| BG0878 | Low | config.py show prints null for keys whose default lives only in a reader's code - not-stop-ship, ruled by Claude (orchestrator) |
| BG0882 | Low | harness_project_slug does not truncate a long project path or map non-BMP characters as the harness does - not-stop-ship, ruled by Claude (orchestrator) |
| BG0885 | Low | critic.py record writes a finding into critic-verdicts.md unescaped, so markdown-shaped text breaks the lint - not-stop-ship, ruled by Claude (orchestrator) |
| BG0886 | Low | The done gate's own refusal messages still print a v3 id as its hyphenless comparison key - not-stop-ship, ruled by Claude (orchestrator) |
| BG0887 | Low | The review command's dashboard and JSON show a per-document health percentage that no code computes - not-stop-ship, ruled by Claude (orchestrator) |
| BG0888 | Low | help/gate.md says the commit-msg hook snippet degrades honestly with no script, but it blocks - not-stop-ship, ruled by Claude (orchestrator) |
| BG0889 | Low | A padded index table holding a wide character still fails MD060 after a row in it is rewritten - not-stop-ship, ruled by Claude (orchestrator) |
| retro-extract | close gap | LC-005 recurred but its CR was not filed: triage session cap reached (20 findings filed this session) - refusing to file more. Fail loud, not silent drop. The counter is keyed on 'RUN-01M3VF2J', and it resets when that key moves: close this run and open the next, or set SDLC_TRIAGE_SESSION to name a session of your own. Raising triage.session_cap moves the wall rather than removing it. Triaging the backlog does NOT help - it decrements nothing, and offering it as an exit was false at the moment it was read. |
| retro-extract | close gap | lessons: 0 hit(s) from cited REJECTs |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3VF2J.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 2,350,747 |

Total 2,350,747, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 9 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 36913650209/36909223880/36906324592/36902763151/36898472211/36890016236/36861303010/36853267621/36849337681 - 9 push-triggered run(s) on main in the run window |
| Lead time for changes | 9h 26m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 111 commit(s) |
| Change failure rate | 11% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | forge runs 36913650209/36909223880/36906324592/36902763151/36898472211/36890016236/36861303010/36853267621/36849337681 - 9 deployment(s); 1 failed on 481ef5019fa3c6aa859678bd71e251856509e2d6 |
| Time to restore | -4h 20m | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | forge runs 36890016236/36861303010 - red then green on main |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 176,417 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 0 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

10 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 6 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 0 | 1 | 1 candidate catch(es) over 3 runs |
| stamps-staged | 3 | 0 | 3 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| style | 0 | 0 | 0 | 2 candidate catch(es) over 3 runs |
| unit-tests | 4 | 2 | 2 | 4 candidate catch(es) over 3 runs |

### Lessons

7 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-005 | repair breaks its neighbour | active | 1 | 2 |
| LC-010 | the push gate and CI disagree on the runner | active | 1 | 1 |
| LC-011 | widen-after-brief | active | 0 | 0 |
| LC-012 | a reviewer's clone cannot see writes into the main repo | active | 0 | 0 |
| LC-013 | suite verdict before the commit | active | 0 | 0 |
| LC-014 | paperwork during a build | active | 0 | 0 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
