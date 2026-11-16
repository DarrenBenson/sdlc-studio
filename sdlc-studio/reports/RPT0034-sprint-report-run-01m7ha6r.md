# Sprint Report: RUN-01M7HA6R

## Goal

A head of engineering upgrades to 6.4 from notes, pages and specs that match the code, nothing High open

**Verdict: Judged achieved** - v6.4.0 is cut: notes, pages and specs match the code; the 6.4.0 CHANGELOG re-cut so each of 133 entries stands alone; no High or Critical finding open (known_issues bar holds). Tag and publish stay with the operator; docs/known-issues.md must be rewritten before the tag.

> **Run:** 2026-11-16T04:37:45Z to 2026-11-16T10:11:22Z (5.6h)
> **Verified on:** 6296d16b31819a689717a2484a91912df4459e7c   **Fingerprint:** 2c27b3912b625cf6

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 34 | 34 | 1.0x | 10 of 10 delivered unit(s) |
| Minutes | 198.5 | 515.8 | 2.6x | measured active minutes (spans or agent minutes) against their forecast, over the 10 of 10 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 318.3 | 333.6 | 1.05x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0029, RPT0030, RPT0031, RPT0032, RPT0033), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 28,675,566 | 25,883,430 | 0.9x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 3,977,701 (input 2,660 x1, output 1,129,656 x5, cache write 5m 2,534,555 x1.25, cache write 1h 310,830 x2, cache read 164,426,365 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0143, RETRO0144, RETRO0145, RETRO0146, RETRO0147) |
| Tokens | 6,332,568 | 3,977,701 | 0.63x | the whole run: forecast over 10 of 10 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 12 delegated total(s) supplied are not added |
| Priced per point | 843,399 | 761,277 | 0.9x | the Priced cost row over the 34 point(s) of the 10 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0143, RETRO0144, RETRO0145, RETRO0146, RETRO0147) |
| Dollar cost | $114.70 | $70.65 | 0.62x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.37 | $2.08 | 0.62x | the Dollar cost row over the 34 point(s) of the 10 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1493 | $5.92 estimated | 29.2 | 73.4 | 931,260 | 331,993 agent tokens | 2,127,768 priced |
| BG1487 | $0.8052 estimated | 5.8 | 25.2 | 186,252 | 60,574 agent tokens, split by points | 260,883 priced, split by points |
| BG1494 | $0.8052 estimated | 5.8 | 24.6 | 186,252 | 60,574 agent tokens, split by points | 260,883 priced, split by points |
| US1170 | $4.24 estimated | 29.2 | 53.6 | 931,260 | 276,086 agent tokens | 1,424,051 priced |
| US1171 | $7.17 estimated | 29.2 | 60.9 | 931,260 | 315,502 agent tokens | 2,796,986 priced |
| US1172 | $5.95 estimated | 29.2 | 56.2 | 931,260 | 310,993 agent tokens | 2,207,334 priced |
| US1173 | $5.84 estimated | 29.2 | 89.3 | 931,260 | 324,091 agent tokens, split by points | 2,107,557 priced, split by points |
| BG1501 | $2.34 estimated | 11.7 | 53.4 | 372,504 | 129,636 agent tokens, split by points | 843,023 priced, split by points |
| BG1498 | $3.08 estimated | 11.7 | 30.2 | 372,504 | 201,037 agent tokens | 1,034,174 priced |
| BG1503 | $2.62 estimated | 17.5 | 48.9 | 558,756 | 163,373 agent tokens | 901,726 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 7 | 27 |
| Delivered of the plan | 7 | 27 |
| Added mid-run and delivered | 3 of 3 added | 7 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 34.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1493 | 5 | 5 | delivered | 1 |
| BG1487 | 1 | 1 | delivered | 1 |
| BG1494 | 1 | 1 | delivered | 1 |
| US1170 | 5 | 5 | delivered | 1 |
| US1171 | 5 | 5 | delivered | 1 |
| US1172 | 5 | 5 | delivered | 1 |
| US1173 | 5 | 5 | delivered | 1 |
| BG1501 | 2 | 2 | added - D0497: push of 3e7f8cd4 refused; US1170's notes test fails outside a git clone; delivered | 2 |
| BG1498 | 2 | 2 | added - D0498: the push gate's per-module noise check refused ec841a10 though CI's total check passes; delivered | 1 |
| BG1503 | 3 | 3 | added - D0499: 6.4.0's CHANGELOG runs about 60 entries together and leaves BG1498's entry pending; the release epic's paperwork must match; delivered | 1 |

## Known issues handed over

8 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0713 | Medium | Prevent or retire lesson LC-019 (a push-gate guard the per-commit run skips) - not-stop-ship, ruled by orchestrator |
| BG1496 | Low | BG1487's README-opening guard lets a reworded approval claim through, though its docstring says it never would - not-stop-ship, ruled by orchestrator |
| BG1497 | Low | Two config keys the code reads are undocumented: sprint.fresh_session is missing from reference-config.md and pricing.copilot_billing from config-defaults.yaml - not-stop-ship, ruled by orchestrator |
| BG1499 | Low | US1058 still reads Status Ready though run thirteen carried it at the review cap and BG1460 delivered it, and the PRD row naming it says Complete - not-stop-ship, ruled by orchestrator |
| BG1500 | Low | help/retro.md says an escaped defect is charged to the seat whose latest verdict approved, in any run, leaving out the code's limit to verdicts on or before the bug's Created day - not-stop-ship, ruled by orchestrator |
| BG1502 | Low | critic.py self-check record refuses a unit until it claims its changelog.d fragment, though the release cut has already merged that fragment into CHANGELOG.md - not-stop-ship, ruled by orchestrator |
| BG1504 | Low | The sdlc-builder agent card does not confine a builder's clean-up to paths it created, so a builder deleted every tmp.* directory in the shared test temp directory - not-stop-ship, ruled by orchestrator |
| BG1505 | Low | 6.4.0's CHANGELOG says a fragment that opens with a list item folds byte for byte, but compose bullets an ordered item, and no test pins a later list item in a prose entry - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M7HA6R.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 3,977,701 |

Total 3,977,701, of which delegated 2,173,859. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (7 units); reviewer inherit (7 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $70.65 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 631 subagent transcript(s); total agents 18, calls 1,281, priced 25,883,430. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 218 | 6,904,996 | 26.7% | 82.7% | 9.0% | 8.3% | 218,627 | 263,418 |
| builder | 8 | 637 | 11,930,989 | 46.1% | 60.0% | 13.3% | 26.6% | 14,123 | 114,441 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 1 | 122 | 2,033,395 | 7.9% | 67.8% | 11.1% | 21.1% | 14,505 | 114,509 |
| other | 8 | 304 | 5,014,050 | 19.4% | 43.7% | 27.0% | 29.3% | 13,751 | 75,594 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 43831150016/43811980982 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 4h 57m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 26 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 43831150016/43811980982 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 43831150016/43811980982 - no push-triggered run on main concluded failure |

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

2 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 0 | 0 | 0 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 1 | 0 | 1 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 1 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 1 | 38 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 1 | 2 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 1 |
