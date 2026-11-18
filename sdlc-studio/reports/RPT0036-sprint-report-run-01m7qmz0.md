# Sprint Report: RUN-01M7QMZ0

## Goal

A reviewer reading only the front door knows SDLC Studio runs in their own harness, models and change process

**Verdict: Judged partial** - The repository's front door is done: the GitHub About box, the README first screen, docs/harnesses.md, docs/enterprise.md, the skill metadata and llms.txt present SDLC Studio as harness-agnostic with people in the lead, every claim checked against the tree. CR0742 names the website home page as the third front-door surface; it lives in the website's own repository and is delivered by a change request run there next, so a reviewer who lands on the site still reads the old positioning.

> **Run:** 2026-11-18T15:28:33Z to 2026-11-18T20:10:32Z (4.7h)
> **Verified on:** 42348d42c5bbad823a5e39241d8f433e3b75268d   **Fingerprint:** 6a1aad45b3ecb41d

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 25 | 25 | 1.0x | 8 of 8 delivered unit(s) |
| Minutes | 145.9 | 432.5 | 2.96x | measured active minutes (spans or agent minutes) against their forecast, over the 8 of 8 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 246.9 | 282.0 | 1.14x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0031, RPT0032, RPT0033, RPT0034, RPT0035), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 19,855,300 | 19,067,651 | 0.96x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 3,501,882 (input 1,960 x1, output 916,558 x5, cache write 5m 2,026,151 x1.25, cache write 1h 557,213 x2, cache read 108,357,864 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0145, RETRO0146, RETRO0147, RETRO0148, RETRO0149) |
| Tokens | 4,656,300 | 3,501,882 | 0.75x | the whole run: forecast over 8 of 8 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 11 delegated total(s) supplied are not added |
| Priced per point | 794,212 | 762,706 | 0.96x | the Priced cost row over the 25 point(s) of the 8 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0145, RETRO0146, RETRO0147, RETRO0148, RETRO0149) |
| Dollar cost | $79.42 | $54.60 | 0.69x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.18 | $2.18 | 0.69x | the Dollar cost row over the 25 point(s) of the 8 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| US1315 | $0.5998 estimated | 5.8 | 40.4 | 186,252 | 34,264 agent tokens, split by points | 212,965 priced, split by points |
| US1316 | $4.50 estimated | 29.2 | 76.9 | 931,260 | 313,302 agent tokens | 1,465,959 priced |
| US1317 | $4.68 estimated | 29.2 | 48.2 | 931,260 | 280,433 agent tokens | 1,642,830 priced |
| US1318 | $2.50 estimated | 17.5 | 51.6 | 558,756 | 174,735 agent tokens | 815,732 priced |
| US1319 | $1.80 estimated | 17.5 | 50.0 | 558,756 | 102,791 agent tokens, split by points | 638,895 priced, split by points |
| US1320 | $4.07 estimated | 17.5 | 63.5 | 558,756 | 265,066 agent tokens, 1 of 2 agent totals split by points | 1,355,910 priced, 1 of 2 agent totals split by points |
| US1321 | $3.89 estimated | 17.5 | 74.3 | 558,756 | 274,434 agent tokens | 1,294,231 priced |
| BG1599 | $1.94 estimated | 11.7 | 27.7 | 372,504 | 132,955 agent tokens | 634,077 priced |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 7 | 23 |
| Delivered of the plan | 7 | 23 |
| Added mid-run and delivered | 1 of 1 added | 2 |
| Dropped | 0 | 0 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 25.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1315 | 1 | 1 | delivered | 1 |
| US1316 | 5 | 5 | delivered | 2 |
| US1317 | 5 | 5 | delivered | 1 |
| US1318 | 3 | 3 | delivered | 1 |
| US1319 | 3 | 3 | delivered | 1 |
| US1320 | 3 | 3 | delivered | 2 |
| US1321 | 3 | 3 | delivered | 2 |
| BG1599 | 2 | 2 | added - no reason recorded; delivered | 1 |

## Known issues handed over

10 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1591 | Low | The author self-check refuses a documentation page the unit's Affects declares as a claim surface, so a docs unit's claims in its own page cannot be recorded and the land refuses its self-check - not-stop-ship, ruled by orchestrator |
| BG1592 | Low | US1317's enterprise-page tests cannot tell a forecast figure from an actual, miss four network-call shapes, plant no failure for the http address check, and pin no link or key outside the controls section - not-stop-ship, ruled by orchestrator |
| BG1593 | Low | tools/check_links.py does not read docs/enterprise.md, so a broken link or anchor on the page exits 0 - not-stop-ship, ruled by orchestrator |
| BG1594 | Low | sprint lane land records the builder's agent id as the self-check author instead of the building seat, so lane accept writes a verdict row the retro cannot score as a seat's - not-stop-ship, ruled by orchestrator |
| BG1595 | Low | sprint lane brief --units joins comma-separated ids into one id and refuses it, instead of splitting on commas or saying the ids are space-separated - not-stop-ship, ruled by orchestrator |
| BG1596 | Low | critic.py record calls a repair builder whose prompt names the verdict path the agent 'briefed with' the verdict, and reports the verdict's provenance as unknown - not-stop-ship, ruled by orchestrator |
| BG1597 | Low | docs/harnesses.md's install-path check accepts the global and project folders in either order, its Claude Code live-reload cell rests on one CLAUDE.md sentence, and two cells cite a file that does not hold the claim - not-stop-ship, ruled by orchestrator |
| BG1598 | Low | README install table labels the GitHub Copilot row 'Copilot' because test_install_copilot_global.py pins that exact label, so the README and docs/harnesses.md name the harness differently - not-stop-ship, ruled by orchestrator |
| BG1600 | Low | test_skill_metadata_neutral.py passes 'must be installed' and 'exclusive to' requirement wordings, cannot tell a fallback from its denial, and leaves four helper branches unpinned - not-stop-ship, ruled by orchestrator |
| BG1601 | Low | sprint plan opened run seventeen although its goal had no seat review, the recorded one being an earlier run's goal, and the close then refuses goal-seat-reviewed past its window - not-stop-ship, ruled by operator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson (entered under delegation, authorised by decision D0535) | 2026-11-18T20:24:04Z | 6a1aad45b3ecb41d |

Signing records the principal, the date and this report's fingerprint against RUN-01M7QMZ0.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 3,501,882 |

Total 3,501,882, of which delegated 1,577,980. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Effort.** The reasoning effort each unit's agents were dispatched at, as the plan this run was
opened from stamped it: builder inherit (7 units); reviewer inherit (7 units).

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $54.60 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 711 subagent transcript(s); total agents 16, calls 933, priced 19,067,651. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 201 | 6,769,079 | 35.5% | 75.4% | 16.5% | 8.1% | 259,921 | 256,711 |
| builder | 6 | 395 | 6,357,550 | 33.3% | 53.7% | 15.7% | 30.6% | 14,969 | 88,457 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 3 | 114 | 1,703,048 | 8.9% | 42.0% | 18.9% | 39.0% | 14,883 | 65,050 |
| other | 6 | 223 | 4,237,975 | 22.2% | 37.8% | 28.7% | 33.5% | 14,237 | 76,179 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 2 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 44340630661/44337315809 - 2 push-triggered run(s) on main in the run window |
| Lead time for changes | 2h 45m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 14 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 44340630661/44337315809 - 2 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 44340630661/44337315809 - no push-triggered run on main concluded failure |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 186,252 | velocity-record |
| Minutes per point | 5.84 | measured on claude-opus-5-5: median of RETRO0131, RETRO0132, RETRO0133 |

### Rulings

Persona seats ruled 3 time(s), 0 of them by citing a
precedent; the operator ruled 2 time(s).

### Waivers in force

1 gate(s) were not holding when this page was derived

- **D0533** - rule:sprint-checklist:goal-seat-reviewed (2026-11-18T19:22:52+00:00): Run seventeen's goal was never seat-reviewed before the plan: the review on record was of an earlier run's goal, and sprint plan printed advice and opened the run (BG1601). The window closed at the plan, so the operator authorised this waiver on 2026-11-18 to record the process failure; it is not a judgement that the review was unneeded. [kind: expired] [authorised by: Darren Benson]

### Lane yield

3 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 2 | 0 | 2 | delete candidate: 3 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | delete candidate: 1 refusal(s) over 3 runs and no candidate catch |

### Lessons

5 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-010 | the push gate and CI disagree on the runner | graduating (CR0712) | 0 | 4 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 44 |
| LC-019 | a push-gate guard the per-commit run skips | graduating (CR0713) | 0 | 3 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | graduating (CR0740) | 1 | 3 |
