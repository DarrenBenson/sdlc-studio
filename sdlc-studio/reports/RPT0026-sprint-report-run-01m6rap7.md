# Sprint Report: RUN-01M6RAP7

## Goal

Every supported harness reports a run's cost the same way, in tokens and dollars, per lane and per role

**Verdict: Judged partial** - Every supported CLI harness is now metered on one normalised basis, per lane through lane run and per session through the Copilot, OpenCode and Codex readers, with dollars per model and a per-role table; partial because the role table reads the whole session rather than the run (BG1254), only Claude models are priced so far, a two-model lane session prices at one model (BG1252), and the benchmark cannot yet run a real session (BG1248)

> **Run:** 2026-11-06T11:32:30Z to 2026-11-06T16:25:37Z (4.9h)
> **Verified on:** 61b37dbde1f218a056fab06e14b8606445abbf33   **Fingerprint:** 6e0677f89a693113

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 40 | 40 | 1.0x | 11 of 11 delivered unit(s) |
| Minutes | 227.7 | 801.0 | 3.52x | measured active minutes (spans or agent minutes) against their forecast, over the 10 of 11 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 293.1 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 47,224,491 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 7,735,113 (input 3,730 x1, output 2,193,334 x5, cache write 5m 5,155,366 x1.25, cache write 1h 382,683 x2, cache read 290,445,179 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 7,450,080 | 7,735,113 | 1.04x | the whole run: forecast over 11 of 11 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 16 delegated total(s) supplied are not added |
| Priced per point | not forecast | 1,180,612 | no ratio | the Priced cost row over the 40 point(s) of the 11 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast | NOT MEASURED - no model the reading names is in the price table: mixed (not priced: the reading spans more than one model and carries no per-model split) | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-06 |
| Dollars per point | not forecast | NOT MEASURED - no model the reading names is in the price table: mixed (not priced: the reading spans more than one model and carries no per-model split) | no ratio | the Dollar cost row over the 40 point(s) of the 11 delivered unit(s); price table effective 2026-11-06 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| US1122 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 17.5 | 29.4 | 558,756 | 227,093 agent tokens | 950,026 priced |
| US1125 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 17.5 | 63.7 | 558,756 | 221,357 agent tokens | 1,080,403 priced |
| US1124 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 17.5 | 114.4 | 558,756 | 353,868 agent tokens | 1,550,599 priced |
| US0987 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 29.2 | 63.0 | 931,260 | 237,589 agent tokens | 1,399,598 priced |
| US1123 | $11.40 estimated | 29.2 | 150.6 | 931,260 | 715,753 agent tokens | 4,071,172 priced |
| US1126 | $6.07 estimated | 29.2 | 105.9 | 931,260 | 391,723 agent tokens | 2,089,528 priced |
| US1128 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 29.2 | 72.2 | 931,260 | 392,138 agent tokens | 1,934,040 priced |
| US1127 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 17.5 | 61.1 | 558,756 | 191,749 agent tokens | 970,293 priced |
| US0988 | NOT MEASURED - no model the reading names is in the price table: no model named (not priced: the reading names no model) | 29.2 | 92.1 | 931,260 | 303,412 agent tokens | 1,494,860 priced |
| BG1238 | $2.64 estimated | 11.7 | 48.7 | 372,504 | 191,701 agent tokens | 879,926 priced |
| BG1255 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1255 --delegated-minutes M` | 186,252 | NOT MEASURED - no In Progress span and no agent total tagged to it - record one with `retro.py accuracy --delegated-tokens N --delegated-unit BG1255 --delegated-minutes M` | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1255 --agent A` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 9 | 37 |
| Delivered of the plan | 9 | 37 |
| Added mid-run and delivered | 2 of 2 added | 3 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 40.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1122 | 3 | 3 | delivered | 1 |
| US1125 | 3 | 3 | delivered | 1 |
| US1124 | 3 | 3 | delivered | 2 |
| US0987 | 5 | 5 | delivered | 1 |
| US1123 | 5 | 5 | delivered | 2 |
| US1126 | 5 | 5 | delivered | 2 |
| US1128 | 5 | 5 | delivered | 2 |
| US1127 | 3 | 3 | delivered | 1 |
| US0988 | 5 | 5 | delivered | 2 |
| BG1238 | 2 | 2 | added - D0413: the push gate refused the landed units; the run cannot push or close green without it; delivered | 2 |
| BG1255 | 1 | 1 | added - D0414: the push gate refused US1123's unconfined git call; delivered | 1 |

## Known issues handed over

32 open finding(s) raised in the run, 1 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1248 | High | The benchmark runner cannot authenticate a real Claude Code or Codex run once it empties their config directories, and it accepts a `--dest` inside a git work tree whose skills and repository the session then reaches - deferred, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1249 | High | The suite's root `conftest.py` isolates neither `HOME` nor `XDG_DATA_HOME`, so suite tests and reviewer mutant runs open the operator's live harness stores - deferred, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0670 | High | Run each sprint wave, and the close, in a fresh orchestrator session started from a bounded on-disk resume brief, so no session carries earlier waves or the planning conversation - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0671 | High | Give the commit hook a sweep lane that always runs the cheap repo-wide sweep tests and refuses a staged new test module without a `test-census-subject` marker, so a sweep red is found at commit rather than at review or push - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0672 | High | Add a deterministic `sprint.py drive` loop that advances each unit's lane through land, brief, review, accept, price and paperwork, lands several staged worktrees as one commit, and wakes the model only at a refusal, a REJECT, a conflict or a wave end - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0673 | High | Replace the author's and the reviewer's hand-rolled mutation passes with one shipped runner (`mutation.py` with drop-conjunct and prose-polarity operators, plus arbitrary file, old and new edits), and have `critic.py self-check record` take its report and refuse unanswered survivors - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0674 | High | Ship restricted-tool agent definitions for builders, reviewers and repairs and spawn every lane and review with them, carrying a hand-back contract (commands in the foreground, at most three lines, detail on disk) and the run's builder notes folded into the shipped lane brief - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1240 | Medium | US0988's OpenCode meter treats a present but unreadable store as absent, against the token-meter contract, and its docstring says a read leaves the write-ahead log alone - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1242 | Medium | US1123's dollar report re-prices an unsigned page from the live price table, so `sprint sign` refuses it after a price revision, and its close wiring and end-date rule are unpinned - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1245 | Medium | US1126's `sprint lane run` leaves a timed-out lane's children staging in the worktree, an in-flight marker after its own refusal, and a branch that refuses the next run - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1246 | Medium | US1127's Codex meter ignores `CODEX_HOME`, leaves its workspace boundary unpinned, and its AC3 test names a timeout mutant it cannot kill - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1252 | Medium | A lane run session that used two models is priced entirely at the rate of the model with the most tokens - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1254 | Medium | sprint cost --anatomy reads the whole session, not the open run's window, so it cannot price one run inside a long-lived session - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1256 | Medium | test_lane_run.py runs git unconfined through a local name and inside its fake CLI script, where the unconfined-git sweep cannot see it - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415's grounds: not a regression of behaviour this run claimed) |
| CR0675 | Medium | Ship a hostile-runtime fixture kit that every change to the verifier core runs: a group SIGTERM and SIGINT to the caller, nested `run_verifier` callers, a consumer pytest.ini with addopts -m and filterwarnings = error beside a pytest11 plugin, a shallow clone, a non-Claude harness environment and an over-long Verify token - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0676 | Medium | Generate each changelog.d fragment from the unit's title and acceptance criteria with one command instead of hand-writing it, so builders stop learning the format and the fragment stops over-claiming - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0677 | Medium | Budget every always-loaded instruction file by size: cut AGENTS.md to at most 7,000 chars and the consuming-project template to at most 5,000 chars, gate both and SKILL.md's token size, and recommend a project settings file that disables unused plugins for delivery sessions - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0678 | Medium | Add `repo_map.py outline` and `where` from the existing symbol index, and have the lane and critic briefs name each target symbol with its line range, so agents stop spending a fifth of their calls locating code - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0679 | Medium | Make the critic brief a complete review packet: claim surfaces first in the capped diff with the full diff written beside it, a one-line `--out` delivery read in one call, verifier and selected-test results computed at brief time against a current verify stamp, and a round-2 rejoinder scoped to the repair - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0680 | Medium | Batch same-wave units of at most 3 points into one reviewer, up to three units with one brief and one verdict file each, and let `critic.py record` accept a round-2 verdict from a fresh reviewer under its own name - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0682 | Medium | Make the author self-check prove each acceptance criterion at the observable it names through the shipped entry point, list the docs outside Affects that name what the diff changed, require a captured producer sample for a unit that parses another tool's output, and tag each blocking finding with its defect class - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0683 | Medium | Fix three run-seven frictions in which a shipped step leaves state the next step refuses: `lane land` checks the self-check hand-in only after it commits, `verify_ac run` in a builder worktree stamps the story file outside the unit's Affects, and `file_finding --parent` leaves the parent RFC's spawned-work cell unsynced - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0684 | Medium | Prevent or retire lesson LC-015 (a retirement outruns the deletion) |
| BG1239 | Low | US0987's Copilot meter leaves its git-root-over-cwd preference unpinned and counts `includes_subagents: False` on trust - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1241 | Low | US1122's price table leaves ten defensive branches unpinned, promises a date format its parser does not hold to, and prices a bare `cost()` call without the project's overrides - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1243 | Low | US1124's cost anatomy leaves four rules unpinned: the per-component maximum, the CLI harness fallback and two role assignments - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1244 | Low | US1125's harness usage parser raises `AttributeError` on a usage container that is not an object, and three of its rules are unpinned - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1247 | Low | US1128's benchmark runner kills only the CLI on a timeout, never cross-checks Claude Code's own dollar total, and leaves its wall time, timeout and skill switches unpinned - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1250 | Low | Fourteen `tools/tests` modules strip every `GIT_*` variable from a child's environment, dropping the conftest's `maintenance.auto` pin and reopening the BG0711 teardown race - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1251 | Low | Three lane frictions each cost a hand-fix: an in-flight warning per sibling lane on every brief, a hand-in fragment not linted before the commit, and a hand-in line that names its fields but not the values the record accepts - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| BG1253 | Low | lib/lanes.py clears only 7 of the 11 repo-locating git variables before it runs a lane - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| CR0681 | Low | Have the commit path write the Refs and Mentions trailers it now refuses for, make every tool that writes markdown emit lint-clean output, and print one line on success from the hooks and the commands agents filter by hand - not-stop-ship, ruled by Claude Opus 5.5 (orchestrator, D0415) |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 1 unruled, 0 malformed row(s) |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M6RAP7.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 7,735,113 |

Total 7,735,113, of which delegated 3,226,383. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 326 subagent transcript(s); total agents 327, calls 26,112, priced 845,296,112. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 6,249 | 352,407,875 | 41.7% | 78.2% | 13.9% | 7.9% | 49,642 | 445,023 |
| builder | 10 | 611 | 12,158,389 | 1.4% | 54.9% | 16.5% | 28.6% | 33,955 | 111,837 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 6 | 235 | 4,262,056 | 0.5% | 51.1% | 20.0% | 28.9% | 34,482 | 95,570 |
| other | 310 | 19,017 | 476,467,792 | 56.4% | 58.9% | 35.5% | 5.7% | 38,420 | 154,616 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 1 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 42213109662 - 1 push-triggered run(s) on main in the run window |
| Lead time for changes | 4h 6m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 17 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 42213109662 - 1 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 42213109662 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
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
| gate | 1 | 0 | 1 | delete candidate: 5 refusal(s) over 3 runs and no candidate catch |
| markdown | 2 | 0 | 2 | delete candidate: 8 refusal(s) over 3 runs and no candidate catch |
| message-refs | 0 | 0 | 0 | delete candidate: 7 refusal(s) over 3 runs and no candidate catch |
| style | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

3 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | graduating (CR0684) | 1 | 2 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 1 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 29 |
