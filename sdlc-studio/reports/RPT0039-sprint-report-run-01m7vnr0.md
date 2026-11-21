# Sprint Report: RUN-01M7VNR0

## Goal

Persona cards meet an enforced standard, each seat's goal brief uses its own card, and persona docs match the code.

**Verdict: Judged partial** - Partial. Clause two (each seat's goal brief uses its own card) is achieved by all three close-time seats; clause three (persona docs match the code) by two of three, product reading partial over BG1669's missing persona_review.py owed entry. Clause one is partial by all three: the enforced standard holds (persona_review.py check blocks=0, and every entry point that frames from a card refuses a held one), but this repository's own seven cards carry no Evidence section and are owed a review (BG1666), so the cards meet the blocking rules only. The close panel reads the partial answers as unanswered (BG1673).

> **Run:** 2026-11-20T05:06:51Z to 2026-11-20T19:09:26Z (14.0h)
> **Verified on:** c87246c4ef2b54dd3269a40e15feccd4c2612658   **Fingerprint:** c091c6110ebbbc71

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 58 | 58 | 1.0x | 20 of 20 delivered unit(s) |
| Minutes | 338.6 | 2886.6 | 8.53x | measured active minutes (spans or agent minutes) against their forecast, over the 20 of 20 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 602.0 | 842.6 | 1.4x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0034, RPT0035, RPT0036, RPT0037, RPT0038), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 44,236,948 | 61,652,338 | 1.39x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 11,239,313 (input 5,186 x1, output 2,140,042 x5, cache write 5m 8,421,453 x1.25, cache write 1h 672,632 x2, cache read 390,748,613 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0148, RETRO0149, RETRO0150, RETRO0151, RETRO0152) |
| Tokens | 10,802,616 | 11,239,313 | 1.04x | the whole run: forecast over 20 of 20 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 25 delegated total(s) supplied are not added |
| Priced per point | 762,706 | 1,062,971 | 1.39x | the Priced cost row over the 58 point(s) of the 20 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0148, RETRO0149, RETRO0150, RETRO0151, RETRO0152) |
| Dollar cost | $176.95 | $167.06 | 0.94x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.05 | $2.88 | 0.94x | the Dollar cost row over the 58 point(s) of the 20 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1002 | $1.47 estimated | 11.7 | 135.2 | 372,504 | 73,292 agent tokens, split by points | 550,526 priced, split by points |
| BG1015 | $2.02 estimated | 11.7 | 54.9 | 372,504 | 105,907 agent tokens, split by points | 759,335 priced, split by points |
| BG1472 | $2.02 estimated | 11.7 | 56.7 | 372,504 | 105,906 agent tokens, split by points | 759,334 priced, split by points |
| BG1535 | $2.20 estimated | 17.5 | 134.6 | 558,756 | 109,938 agent tokens, split by points | 825,789 priced, split by points |
| BG1536 | $2.02 estimated | 11.7 | 58.1 | 372,504 | 105,906 agent tokens, split by points | 759,334 priced, split by points |
| US1036 | $3.47 estimated | 17.5 | 69.0 | 558,756 | 310,073 agent tokens | 1,130,912 priced |
| US1039 | $2.20 estimated | 17.5 | 133.9 | 558,756 | 109,939 agent tokens, split by points | 825,790 priced, split by points |
| US1040 | $3.47 estimated | 17.5 | 220.5 | 558,756 | 293,541 agent tokens | 1,149,247 priced |
| US1046 | $2.20 estimated | 17.5 | 134.3 | 558,756 | 109,938 agent tokens, split by points | 825,789 priced, split by points |
| US1052 | $7.64 estimated | 29.2 | 143.5 | 931,260 | 550,580 agent tokens, split by points | 2,795,861 priced, split by points |
| US1053 | $5.21 estimated | 29.2 | 82.2 | 931,260 | 382,878 agent tokens | 1,807,667 priced |
| US1054 | $1.86 estimated | 11.7 | 41.2 | 372,504 | 131,507 agent tokens | 615,480 priced |
| US1055 | $22.47 estimated | 29.2 | 245.7 | 931,260 | 2,250,060 agent tokens | 7,660,882 priced |
| US1056 | $4.59 estimated | 11.7 | 272.2 | 372,504 | 191,630 agent tokens, split by points | 1,813,808 priced, split by points |
| US1057 | $11.48 estimated | 29.2 | 272.7 | 931,260 | 479,073 agent tokens, split by points | 4,534,522 priced, split by points |
| US1322 | $6.89 estimated | 17.5 | 273.1 | 558,756 | 287,444 agent tokens, split by points | 2,720,712 priced, split by points |
| BG1655 | $7.56 estimated | 17.5 | 253.3 | 558,756 | 565,563 agent tokens, 1 of 2 agent totals split by points | 2,657,105 priced, 1 of 2 agent totals split by points |
| BG1660 | $2.75 estimated | 17.5 | 147.0 | 558,756 | 236,654 agent tokens | 936,828 priced |
| BG1663 | $1.23 estimated | 5.8 | 33.9 | 186,252 | 97,403 agent tokens | 378,941 priced |
| BG1664 | $1.07 estimated | 5.8 | 124.6 | 186,252 | 42,989 agent tokens, split by points | 428,864 priced, split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 16 | 50 |
| Delivered of the plan | 16 | 50 |
| Added mid-run and delivered | 4 of 4 added | 8 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 58.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1002 | 2 | 2 | delivered | 2 |
| BG1015 | 2 | 2 | delivered | 1 |
| BG1472 | 2 | 2 | delivered | 1 |
| BG1535 | 3 | 3 | delivered | 1 |
| BG1536 | 2 | 2 | delivered | 1 |
| US1036 | 3 | 3 | delivered | 2 |
| US1039 | 3 | 3 | delivered | 2 |
| US1040 | 3 | 3 | delivered - discharged after it was carried at the review cap: BG1660 | 3 |
| US1046 | 3 | 3 | delivered | 1 |
| US1052 | 5 | 5 | delivered | 1 |
| US1053 | 5 | 5 | delivered | 1 |
| US1054 | 2 | 2 | delivered | 1 |
| US1055 | 5 | 5 | delivered | 3 |
| US1056 | 2 | 2 | delivered | 3 |
| US1057 | 5 | 5 | delivered | 3 |
| US1322 | 3 | 3 | delivered | 2 |
| BG1655 | 3 | 3 | delivered - discharged after it was carried at the review cap: BG1663 | 3 |
| BG1660 | 3 | 3 | added - no reason recorded; delivered | 1 |
| BG1663 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG1664 | 1 | 1 | added - no reason recorded; delivered | 1 |

## Known issues handed over

23 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| CR0749 | Medium | sprint plan names existing tests outside a unit's Affects that exercise the code it changes, so grooming widens Affects before build - not-stop-ship, ruled by orchestrator |
| BG1650 | Low | persona_goals reads an unclosed <!-- inside code as a comment that hides a card's End goals, and attaches a nested Verify to whichever goal came last - not-stop-ship, ruled by orchestrator |
| BG1651 | Low | The End-goal scope lint misdescribes `**` and suggests a replacement for a bare `**` that names no file - not-stop-ship, ruled by orchestrator |
| BG1652 | Low | Five behaviours persona_goals and its reference state have no test: a mutant of each survives - not-stop-ship, ruled by orchestrator |
| BG1653 | Low | BG1002's _live_run comment claims a missing run state is handled, and four branches of the live-run read have no test - not-stop-ship, ruled by orchestrator |
| BG1654 | Low | A reviewer cannot check a verdict file before hand-back: critic.py record refuses an odd backtick count only when the operator records it - not-stop-ship, ruled by orchestrator |
| BG1656 | Low | The consult's load step never classifies a flat Served card, and BG1535's tests accept the stakeholder declaration anywhere on the card - not-stop-ship, ruled by orchestrator |
| BG1657 | Low | file_finding writes a title's bare double asterisk unescaped into the artefact and its index row, which markdownlint refuses - not-stop-ship, ruled by orchestrator |
| BG1658 | Low | The goal brief's no-current-batch answer names a goal-review flag that does not exist, and two of US1036's framing branches have no test - not-stop-ship, ruled by orchestrator |
| BG1659 | Low | Five behaviours persona_review.py and its reference page state have no test: a mutant of each passes test_persona_standard.py - not-stop-ship, ruled by orchestrator |
| BG1661 | Low | A high-risk unit moves to Done on the first seat's APPROVE, so the second seat's REJECT lands past the round cap and carries the unit instead of repairing it - not-stop-ship, ruled by orchestrator |
| BG1662 | Low | seat-persona-unknown still reads a two-word product surface marked with a role, such as Ship the Admin Console (Primary), as an unknown persona - not-stop-ship, ruled by orchestrator |
| BG1665 | Low | critic.py record refuses a parallel second seat's verdict once the first seat's REJECT is recorded, so its REJECT never reaches the ledger - not-stop-ship, ruled by orchestrator |
| BG1666 | Low | This repository's seven persona and seat cards carry no Evidence section, so persona_review.py check reports persona-evidence on each - not-stop-ship, ruled by orchestrator |
| BG1667 | Low | persona_resolve.py resolve tracebacks with UnicodeDecodeError on a seat card that is not valid UTF-8, where critic.py brief refuses it cleanly - not-stop-ship, ruled by orchestrator |
| BG1668 | Low | personas.standard: report does not cover the goal review's refusal of a traced persona card, which still refuses under report mode - not-stop-ship, ruled by orchestrator |
| BG1669 | Low | reference-scripts-review.md does not describe persona_review.py owed - not-stop-ship, ruled by orchestrator |
| BG1670 | Low | persona_review.remedy names a brief command for a card held by a blocking rule, whose PASS persona_review.py record then refuses - not-stop-ship, ruled by orchestrator |
| BG1671 | Low | init.py writes no personas.standard, so a project created at the persona-standard release is switched to report mode by its first later project upgrade - not-stop-ship, ruled by orchestrator |
| BG1672 | Low | changelog.d/US1057.md says validate.py personas and seats exited with a UnicodeDecodeError traceback, though they printed a one-line Error and aborted the check - not-stop-ship, ruled by orchestrator |
| BG1673 | Low | verdict_polarity reads a seat's 'partial' as unclear, so a goal clause every seat answered partial reads UNANSWERED at the close - not-stop-ship, ruled by orchestrator |
| BG1674 | Low | No test pins card-not-utf8's severity split (a warning for persona cards, an error for seat cards) or the exit code validate.py seats gives for it - not-stop-ship, ruled by orchestrator |
| BG1675 | Low | The goal trace reads a persona card that is not UTF-8 as empty, so a goal naming that persona is briefed as naming nobody and its card-not-utf8 hold never refuses the goal review - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0545) | 2026-11-21T08:22:23Z | c091c6110ebbbc71 |

Signing records the principal, the date and this report's fingerprint against RUN-01M7VNR0.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 11,239,313 |

Total 11,239,313, of which delegated 6,540,221. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (20 units); reviewer inherit (20 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $165.65 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $1.40 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 827 subagent transcript(s); total agents 31, calls 2,473, priced 61,652,338. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 477 | 14,565,426 | 23.6% | 81.8% | 9.2% | 9.0% | 327,170 | 251,171 |
| builder | 11 | 1,130 | 27,459,569 | 44.5% | 60.8% | 21.1% | 18.1% | 14,771 | 151,840 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 3 | 274 | 6,477,157 | 10.5% | 65.9% | 12.0% | 22.0% | 15,169 | 158,125 |
| other | 16 | 592 | 13,150,186 | 21.3% | 47.1% | 30.1% | 22.8% | 19,317 | 110,023 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44781502190/44732069732 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 11h 27m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 29 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44781502190/44732069732 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44781502190/44732069732 - no push-triggered run on main concluded failure |

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
| gate | 1 | 0 | 1 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 56 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 0 | 3 |
