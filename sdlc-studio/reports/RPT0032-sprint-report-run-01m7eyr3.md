# Sprint Report: RUN-01M7EYR3

## Goal

A head of engineering sees each review seat's record, and an escaped defect traced to the approval that missed it

**Verdict: Judged achieved** - A head of engineering now sees each review seat's record (its approvals, rounds and the defects found after it approved) and an escaped defect traced to the unit and approval that let it through; the seats' learnings go live only from a signed run, after another seat approves them. US1058 was carried at the review cap and delivered through BG1460.

> **Run:** 2026-11-15T06:40:34Z to 2026-11-15T20:14:25Z (13.6h)
> **Verified on:** dbae860fbc1879bec96ff88cc83faf4a45e1a2e4   **Fingerprint:** dfa4679614cfeb00

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 54 | 54 | 1.0x | 16 of 16 delivered unit(s) |
| Minutes | 297.7 | 3725.4 | 12.51x | measured active minutes (spans or agent minutes) against their forecast, over the 14 of 16 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | 406.3 | 813.9 | 2.0x | the run's minutes, start to end, so waiting counts; never compared with the Minutes row's active work; forecast: the plan's points over points per elapsed hour (measured: median points per elapsed hour of RPT0027, RPT0028, RPT0029, RPT0030, RPT0031), never the active-minutes forecast, which the Minutes row compares; forecasts are descriptive: each is the plan's points times a rate measured from earlier runs, and no ratio refuses or warns |
| Priced cost | 45,659,268 | 46,679,710 | 1.02x | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 7,720,036 (input 3,876 x1, output 1,666,066 x5, cache write 5m 4,913,754 x1.25, cache write 1h 1,136,340 x2, cache read 299,306,319 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0141, RETRO0142, RETRO0143, RETRO0144, RETRO0145) |
| Tokens | 10,057,608 | 7,720,036 | 0.77x | the whole run: forecast over 16 of 16 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 23 delegated total(s) supplied are not added |
| Priced per point | 845,542 | 864,439 | 1.02x | the Priced cost row over the 54 point(s) of the 16 delivered unit(s), in priced input-equivalent tokens per point; forecast: the plan's points times its priced per point rate (measured: median priced per point of RETRO0141, RETRO0142, RETRO0143, RETRO0144, RETRO0145) |
| Dollar cost | $182.64 | $126.86 | 0.69x | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |
| Dollars per point | $3.38 | $2.35 | 0.69x | the Dollar cost row over the 54 point(s) of the 16 delivered unit(s); price table effective 2026-11-12; forecast: the plan's priced forecast at claude-opus-5-5's input price per million, price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| US1059 | $4.10 estimated | 29.2 | 141.5 | 931,260 | 265,424 agent tokens, split by points | 1,513,196 priced, split by points |
| US1061 | $2.29 estimated | 17.5 | 97.3 | 558,756 | 117,875 agent tokens, split by points | 849,245 priced, split by points |
| US1062 | $3.82 estimated | 29.2 | 98.7 | 931,260 | 196,457 agent tokens, split by points | 1,415,408 priced, split by points |
| US1064 | $4.14 estimated | 29.2 | 616.8 | 931,260 | 279,907 agent tokens | 1,396,372 priced |
| US1065 | $7.50 estimated | 17.5 | 630.8 | 558,756 | 452,430 agent tokens, 1 of 2 agent totals split by points | 2,727,542 priced, 1 of 2 agent totals split by points |
| US1066 | $10.44 estimated | 29.2 | 592.1 | 931,260 | 659,978 agent tokens | 3,846,714 priced |
| US1067 | $5.87 estimated | 29.2 | 605.5 | 931,260 | 325,713 agent tokens, 1 of 2 agent totals split by points | 2,173,323 priced, 1 of 2 agent totals split by points |
| US1068 | $5.87 estimated | 29.2 | 606.1 | 931,260 | 325,712 agent tokens, 1 of 2 agent totals split by points | 2,173,323 priced, 1 of 2 agent totals split by points |
| US1157 | $2.57 estimated | 17.5 | 75.2 | 558,756 | 133,667 agent tokens, split by points | 966,498 priced, split by points |
| US1158 | $2.57 estimated | 17.5 | 76.6 | 558,756 | 133,667 agent tokens, split by points | 966,497 priced, split by points |
| US1159 | $2.19 estimated | 11.7 | 69.8 | 372,504 | 141,137 agent tokens | 760,857 priced |
| BG1459 | $10.44 estimated | 5.8 | NOT MEASURED - 0 of its 1 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 186,252 | 659,978 agent tokens | 3,846,714 priced |
| BG1460 | $2.78 estimated | 29.2 | 44.9 | 931,260 | 183,255 agent tokens | 938,865 priced |
| BG1468 | $4.02 estimated | 5.8 | 34.9 | 186,252 | 232,437 agent tokens | 1,445,304 priced |
| BG1469 | $4.02 estimated | 5.8 | 35.2 | 186,252 | 232,437 agent tokens | 1,445,304 priced |
| BG1471 | $2.43 estimated | 11.7 | NOT MEASURED - 0 of its 2 tagged agent(s) reported minutes, so its minutes are unknown - an agent's minutes are recorded with its `--delegated-tokens` as `--delegated-minutes M` when it reports, and cannot be added afterwards | 372,504 | 167,550 agent tokens, 1 of 2 agent totals split by points | 827,065 priced, 1 of 2 agent totals split by points |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 12 | 49 |
| Delivered of the plan | 11 | 44 |
| Added mid-run and delivered | 5 of 5 added | 10 |
| Dropped | 1 | 5 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 54.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| US1058 | 5 | 5 | dropped - carried at the review cap: BG1460 | 2 |
| US1059 | 5 | 5 | delivered | 1 |
| US1061 | 3 | 3 | delivered | 1 |
| US1062 | 5 | 5 | delivered | 1 |
| US1064 | 5 | 5 | delivered | 2 |
| US1065 | 3 | 3 | delivered | 2 |
| US1066 | 5 | 5 | delivered | 1 |
| US1067 | 5 | 5 | delivered | 2 |
| US1068 | 5 | 5 | delivered | 2 |
| US1157 | 3 | 3 | delivered | 1 |
| US1158 | 3 | 3 | delivered | 1 |
| US1159 | 2 | 2 | delivered | 1 |
| BG1459 | 1 | 1 | added - Main red on test_command_audit's unjudged-flags ratchet since US1058's repair added persona_memory.py --fields-file; fixed in the US1065/US1066 lane, which adds further persona_memory flags (D0483); delivered | 1 |
| BG1460 | 5 | 5 | added - D0484: repair US1058's review-cap carry in-run; an approval bypass in persona memory stops the run's goal; delivered | 1 |
| BG1468 | 1 | 1 | added - D0485: main red on two boundary tests from this run's persona-memory lanes; delivered | 1 |
| BG1469 | 1 | 1 | added - D0486: built with US1065's repair and BG1468 in one persona-memory lane; delivered | 1 |
| BG1471 | 2 | 2 | added - D0487: set_fields forges a learning's State; built in the persona-memory repair lane; delivered | 2 |

## Known issues handed over

17 open finding(s) raised in the run, 0 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1455 | Medium | escape.py trace counts a Mentions: trailer id as a unit the release shipped, so a commit that only names a unit puts it among the suspects - not-stop-ship, ruled by orchestrator |
| BG1463 | Medium | retro.py seats drops an Escaped-via bug silently when its unit's approval names no seat, has only a REJECT, or post-dates the bug - not-stop-ship, ruled by orchestrator |
| BG1465 | Medium | retro.py seat_misses reads each cited unit's file uncached, so an unbounded window does not finish in ten minutes - not-stop-ship, ruled by orchestrator |
| BG1470 | Medium | lane land runs the full commit hooks, then refuses the rebase over an unstaged author-self-checks.md the builder's self-check left in the worktree - not-stop-ship, ruled by orchestrator |
| BG1472 | Medium | Five branches of the close's learning review and the sign's strike are right by execution but no test fails without them - not-stop-ship, ruled by orchestrator |
| CR0706 | Medium | An incident is triaged into the escaped bugs it caused, the report states escapes per 100 points, and an escape's class reaches only the briefs whose files it matches - not-stop-ship, ruled by orchestrator |
| CR0707 | Medium | sprint lane offers a rebase step that carries a waiting lane's staged work onto a moved main - not-stop-ship, ruled by orchestrator |
| CR0708 | Medium | file_finding writes criteria a plan can take, or marks a bug ungroomed, instead of truncated stubs with no Verify line - not-stop-ship, ruled by orchestrator |
| BG1456 | Low | The escaped-bug Fixed gate's scaffold stripping is untested and matches the scaffold by exact string, and test_file_finding's selector reader test fails outside a git checkout - not-stop-ship, ruled by orchestrator |
| BG1457 | Low | The seat record reads any bracketed word as a seat, lane brief --seat accepts any value, and retro seats counts rounds across deliveries - not-stop-ship, ruled by orchestrator |
| BG1458 | Low | escape.py to-class records a class with no files for a hand-edited bug with no Affects, collapses whitespace inside Affects paths, and the catalogue pages lag the new verb and flags - not-stop-ship, ruled by orchestrator |
| BG1461 | Low | lane brief warns a landed unit under review never returned, and that the tree may already carry its work - not-stop-ship, ruled by orchestrator |
| BG1462 | Low | lane accept records under the self-check's agent author and critic.py record then warns that author lacks the holder (role) form - not-stop-ship, ruled by orchestrator |
| BG1464 | Low | retro.py's own-finding check matches a review word anywhere in Evidence and two of its guards have no test - not-stop-ship, ruled by orchestrator |
| BG1466 | Low | A signed report's signoff principal and signed_at figures still read not yet signed, though the evidence schema says they hold who signed and when - not-stop-ship, ruled by orchestrator |
| BG1467 | Low | A review-cap carry bug copies the carried unit's Affects verbatim, so it declares the unit's changelog fragment, not its own - not-stop-ship, ruled by orchestrator |
| BG1473 | Low | A damaged tracked run record reads on the brief as awaits its run's signature, not as damaged - not-stop-ship, ruled by orchestrator |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| Darren Benson | 2026-11-15T20:17:48Z | dfa4679614cfeb00 |

Signing records the principal, the date and this report's fingerprint against RUN-01M7EYR3.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 7,720,036 |

Total 7,720,036, of which delegated 4,864,566. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $126.86 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 587 subagent transcript(s); total agents 23, calls 1,895, priced 46,679,710. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 319 | 15,337,446 | 32.9% | 79.1% | 14.8% | 6.0% | 626,977 | 384,051 |
| builder | 8 | 808 | 16,478,824 | 35.3% | 63.5% | 14.6% | 21.9% | 13,812 | 131,928 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 5 | 242 | 3,374,307 | 7.2% | 55.1% | 17.6% | 27.2% | 13,688 | 78,848 |
| other | 9 | 526 | 11,489,133 | 24.6% | 47.6% | 27.4% | 25.0% | 16,140 | 108,686 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 1 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 43687192808 - 1 push-triggered run(s) on main in the run window |
| Lead time for changes | 12h 59m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 28 commit(s) |
| Change failure rate | 0% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | forge runs 43687192808 - 1 deployment(s); 0 failed on none |
| Time to restore | no restore needed | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | forge runs 43687192808 - no push-triggered run on main concluded failure |

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
| gate | 1 | 0 | 1 | delete candidate: 7 refusal(s) over 3 runs and no candidate catch |
| markdown | 1 | 0 | 1 | delete candidate: 6 refusal(s) over 3 runs and no candidate catch |

### Lessons

1 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 2 | 35 |
