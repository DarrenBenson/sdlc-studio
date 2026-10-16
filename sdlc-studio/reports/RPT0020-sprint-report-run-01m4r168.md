# Sprint Report: RUN-01M4R168

## Goal

Maya's ledger and signed runs keep what was decided, and her gates say up front what they need and cost.

**Verdict: Judged achieved** - RUN-01M4R168: 18 units, each independently approved at its band's depth; the goal is achieved per the operator's ruling of 2026-10-14 that US1004's approval decides it. Closed on 2026-10-16 without the project lessons log, on the operator's ruling to carry the gap (BG1060).

> **Run:** 2026-10-12T12:35:20Z to 2026-10-16T08:33:39Z (92.0h)
> **Verified on:** fad902aed553ef6905251387ae059a5dfbe5ca01   **Fingerprint:** cf3fd54456d58755

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 38 | 37 | 0.97x | 18 of 18 delivered unit(s) |
| Minutes | 221.9 | NOT MEASURED - no unit carries a measured time (an In Progress span or agent minutes) | NOT MEASURED - needs both a forecast and an actual | the whole run: forecast over 18 of 18 unit(s) planned or added and not dropped; no unit carries both a forecast and a measured time |
| Wall-clock span | not forecast | 5518.3 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Tokens | 5,154,852 | 7,605,066 | NOT MEASURED - withheld - no delegated spend was supplied, so the actual is the main-thread meter alone, which cannot see a delegated agent's spend; each lane records its builder's total with `sprint lane return --tokens N` | the whole run: forecast over 18 of 18 unit(s) planned or added and not dropped; actual is the run meter, a lower bound |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0950 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0950 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0950 --delegated-minutes M` |
| BG1003 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1003 --delegated-minutes M` | 406,962 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1003 --delegated-minutes M` |
| BG1025 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1025 --delegated-minutes M` | 406,962 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1025 --delegated-minutes M` |
| US1003 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1003 --delegated-minutes M` | 406,962 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1003 --delegated-minutes M` |
| US1004 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1004 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1004 --delegated-minutes M` |
| BG0944 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0944 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0944 --delegated-minutes M` |
| BG0945 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0945 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0945 --delegated-minutes M` |
| BG0976 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0976 --delegated-minutes M` | 135,654 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0976 --delegated-minutes M` |
| BG0978 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0978 --delegated-minutes M` | 135,654 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG0978 --delegated-minutes M` |
| US1005 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1005 --delegated-minutes M` | 406,962 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1005 --delegated-minutes M` |
| US1006 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1006 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit US1006 --delegated-minutes M` |
| BG1032 | 17.5 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1032 --delegated-minutes M` | 406,962 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1032 --delegated-minutes M` |
| BG1031 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1031 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1031 --delegated-minutes M` |
| BG1044 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1044 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1044 --delegated-minutes M` |
| BG1045 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1045 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1045 --delegated-minutes M` |
| BG1047 | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1047 --delegated-minutes M` | 135,654 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1047 --delegated-minutes M` |
| BG1053 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1053 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1053 --delegated-minutes M` |
| BG1056 | 11.7 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1056 --delegated-minutes M` | 271,308 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1056 --delegated-minutes M` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 11 | 24 |
| Delivered of the plan | 11 | 24 |
| Added mid-run and delivered | 7 of 7 added | 14 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 37.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0950 | 2 | 2 | delivered | 3 |
| BG1003 | 3 | 3 | delivered | 2 |
| BG1025 | 3 | 2 | delivered | 2 |
| US1003 | 3 | 3 | delivered | 2 |
| US1004 | 2 | 2 | delivered | 4 |
| BG0944 | 2 | 2 | delivered | 1 |
| BG0945 | 2 | 2 | delivered | 1 |
| BG0976 | 1 | 1 | delivered | 2 |
| BG0978 | 1 | 1 | delivered | 1 |
| US1005 | 3 | 3 | delivered | 1 |
| US1006 | 2 | 2 | delivered | 3 |
| BG1032 | 3 | 3 | added - no reason recorded; delivered | 2 |
| BG1031 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG1044 | 2 | 2 | added - operator ruling 2026-10-14: fix BG1044 before BG0993's rounds 3 and 4 are recorded under D0352 and D0353, so the RULING records land under a correct note in the append-only ledger; delivered | 1 |
| BG1045 | 2 | 2 | added - operator ruling 2026-10-14: US1006's carry is fixed in this run, as BG0950's was; delivered | 1 |
| BG1047 | 1 | 1 | added - operator ruling 2026-10-14: the test_status fixture aged into staleness on day 90 and turned main red; fixed in this run so it gets a review; delivered | 1 |
| BG1053 | 2 | 2 | added - the reviewer whose REJECTs carried BG1053 and US1004 approved BG1056, their carry, discharging both carries; re-added as US1006 was (operator delegation 2026-10-15); delivered | 3 |
| BG1056 | 2 | 2 | added - operator delegation 2026-10-15 (complete the sprint autonomously): one bounded closed-world repair of BG1053's carry; if its review does not approve, US1004 is carried to the next run; delivered | 1 |

## Known issues handed over

30 open finding(s) raised in the run, 2 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1050 | Medium | A reviewer id carrying a carriage return or line separator tears its own verdict row - not-stop-ship, ruled by Darren Benson (operator) |
| BG1051 | Medium | The close's chain report cuts every refusal line at 160 characters, hiding which unit is blocked and why - not-stop-ship, ruled by Darren Benson (operator) |
| BG1052 | Medium | A unit whose risk band rises after its review is found under-reviewed only at the close - not-stop-ship, ruled by Darren Benson (operator) |
| BG1054 | Medium | The scheduled corpus-verify lane reads US0892 AC1 red because its job installs no pytest-xdist - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| BG1058 | Medium | The close's dry run names a unit the run cannot end over that the real tree answers - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| BG1059 | Medium | A retro's Batch field is never compared with the run's batch, so a unit added after the retro was scaffolded is left out of the run's measurement and its close accounting - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| BG1060 | Medium | retro extract starts a new project lessons log when the committed one is missing, though the committed digest lists the lessons that log holds - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| CR0638 | Medium | The release verify lane has no vitest batch path, so in a vitest project every criterion is a cold `npx vitest run` spawn and the lane runs at three times its declared 600 s budget - not-stop-ship, ruled by Darren Benson (operator) |
| CR0642 | Medium | Prevent or retire lesson LC-016 (a signed page reads a live source) - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| CR0643 | Medium | Prevent or retire lesson LC-018 (a doc claim checked by reading) - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| BG1030 | Low | Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited - not-stop-ship, ruled by Darren Benson (operator) |
| BG1033 | Low | When sign cannot read the close's carried rows it moves every unit, and the warning it prints has no test - not-stop-ship, ruled by Darren Benson (operator) |
| BG1034 | Low | Sign's predates exemption has no pin, and BG0944's reopen pin and module selection are weaker than they look - not-stop-ship, ruled by Darren Benson (operator) |
| BG1035 | Low | BG0945's test holds the old claim off by one literal phrase, and the untracked first-ruling branch is unstated and unpinned - not-stop-ship, ruled by Darren Benson (operator) |
| BG1036 | Low | BG0978's stub-interpreter test cannot tell sys.executable from the PATH's python3, and checks only an exit code - not-stop-ship, ruled by Darren Benson (operator) |
| BG1037 | Low | A bracket of another type opened inside a pair is not literal, so a ';' the pair encloses is still split, and BG1032's note over-claims inside code spans - not-stop-ship, ruled by Darren Benson (operator) |
| BG1038 | Low | The pre-push keepalive check reads GIT_SSH above core.sshCommand, the reverse of git's order, and asks ssh -G without the configured command's own options - not-stop-ship, ruled by Darren Benson (operator) |
| BG1039 | Low | US1004's one-list test no longer requires `-r` on the suite step, and still checks hand installs against its own list of four packages - not-stop-ship, ruled by Darren Benson (operator) |
| BG1040 | Low | gate_prereqs prints the SDLC_COVERAGE_PYTHON route without reading that interpreter, reads markers without evaluating them, and skips -r lines silently - not-stop-ship, ruled by Darren Benson (operator) |
| BG1041 | Low | The module-alone lane test can never pass on a host with fewer than four cores, and blames the pool for it - not-stop-ship, ruled by Darren Benson (operator) |
| BG1042 | Low | The push preflight's tests leak SDLC_COVERAGE_PYTHON and leave its REFUSES mark and pytest's class unpinned - not-stop-ship, ruled by Darren Benson (operator) |
| BG1043 | Low | The prerequisite check and the gate read pytest-xdist two different ways - not-stop-ship, ruled by Darren Benson (operator) |
| BG1046 | Low | A carry turns a pre-existing finding into a criterion the carried bug can never meet - not-stop-ship, ruled by Darren Benson (operator) |
| BG1048 | Low | forward-port deletes the CHANGELOG.md install.sh ships into the installed copy - not-stop-ship, ruled by Darren Benson (operator) |
| BG1049 | Low | BG1044's ruling-record tests leave the date, the note's once-only rule, the heading anchor and the case boundary unpinned - not-stop-ship, ruled by Darren Benson (operator) |
| BG1055 | Low | A retro scaffolded by the close and committed before the close re-runs turns the release-verify lane red - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| BG1057 | Low | The one-list test's check that ci installs from requirements-dev.txt sits outside its self-tested rules - not-stop-ship, ruled by Claude Opus 5.5 (author), under the operator's delegation of 2026-10-15 |
| CR0639 | Low | A worktree-isolated reviewer that REJECTs cannot be resumed for its round 2 once its worktree is removed, and nothing says to keep it until the review converges - not-stop-ship, ruled by Darren Benson (operator) |
| CR0640 | Low | A reference page edited without regenerating its reading guide passes every commit lane and is found only by the full suite at push - not-stop-ship, ruled by Darren Benson (operator) |
| CR0641 | P3 | A review-round ruling is admitted from any accepted decision about the unit, not one that authorises a round - not-stop-ship, ruled by Darren Benson (operator) |
| lessons-summary | close gap | refused: LESSONS-SUMMARY.md lists 441 lesson(s) the log at /home/darren/code/DarrenBenson/sdlc-studio/sdlc-studio/retros/LESSONS.md does not hold (L-0442: Run each user-facing sentence in a changelog fragment through the CLI before asking for review, as the paperwork reviews already do., L-0441: Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped..., L-0440: A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_` scrub broke... (+438 more)), so this log is not the one the summary was built from. Restore the log from the machine that ran the last close, or merge it, and run this again. Nothing was written. |
| gate | close gap | lessons-summary: LESSONS-SUMMARY.md is STALE - 3 lesson(s) added since it was regenerated: L-0003: Date a fixture from today whenever the code under test reads the real clock, and pin the boundary day as BG1047's reviewer did., L-0002: Before a review, put each changelog claim through the shipped entry point against its strongest negative, and name every mutant a message..., L-0001: Re-derive the review tier at every brief and record, and name an under-depth APPROVE the moment it exists (BG1052).; 441 closed or removed since: L-0442: Run each user-facing sentence in a changelog fragment through the CLI before asking for review, as the paperwork reviews already do., L-0441: Probe a premise with an input whose result differs under each hypothesis, such as a key whose code fallback differs from its shipped..., L-0440: A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_` scrub broke... (+438 more). Regenerate it: scripts/lessons.py summary |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-10-16T10:02:51Z | cf3fd54456d58755 |

Signing records the principal, the date and this report's fingerprint against RUN-01M4R168.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| claude-opus-5-5 | 7,605,066 |

Total 7,605,066, of which delegated NOT MEASURED - no delegated agent supplied a total, which is not the same fact as no work having been delegated. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 14 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 38806484732/38802667038/38798980550/38794197044/38786214345/38563007182/38558849979/38552579156/38419375826/38416059808/38412644951/38407807659/38392645887/38379455382 - 14 push-triggered run(s) on main in the run window |
| Lead time for changes | 79h 44m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 41 commit(s) |
| Change failure rate | 7% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 38806484732/38802667038/38798980550/38794197044/38786214345/38563007182/38558849979/38552579156/38419375826/38416059808/38412644951/38407807659/38392645887/38379455382 - 14 deployment(s); 1 failed on 37fd98d58513ca9dcd866fbb66e6d5f98dcbc825 |
| Time to restore | 0h 52m | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 38552579156/38558849979 - each red streak on main restored by the first push-triggered run created after its first failure that concluded success |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 135,654 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 2 time(s).

### Waivers in force

no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window

### Lane yield

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| markdown | 1 | 0 | 1 | too few runs: 1 of 3 recorded |
| message-refs | 2 | 0 | 2 | too few runs: 1 of 3 recorded |
| repo-writes | 1 | 0 | 1 | too few runs: 1 of 3 recorded |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 1 |
| LC-014 | paperwork during a build | active | 0 | 1 |
| LC-015 | a retirement outruns the deletion | active | 0 | 0 |
| LC-016 | a signed page reads a live source | graduating (CR0642) | 1 | 2 |
| LC-017 | a page-format rule mark nothing round-trips | active | 0 | 0 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 4 | 4 |

### Not measured

Close checklist rows this run gave nothing to measure. Nothing is known to be wrong, so none is
a known issue; nothing is known to be right, so none reads as done.

| Row | State | Why |
| --- | --- | --- |
| cost: Cost, velocity and estimate accuracy | not measured | no per-unit telemetry, no measured run total and no supplied sprint total, so what this sprint cost is not attributable - which is not zero |
