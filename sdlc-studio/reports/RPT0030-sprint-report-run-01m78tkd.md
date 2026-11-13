# Sprint Report: RUN-01M78TKD

## Goal

Lanes land and die cleanly, verifiers never read green wrongly, and every unit's cost is priced.

**Verdict: Judged partial** - All 24 planned units, 49 points, delivered on independent APPROVEs (four after one repair round each). Lanes land and die cleanly (BG1336, BG1337, BG1339, BG1344, BG1261, BG1262) and verifiers no longer read green wrongly or leak (BG1005, BG1009, BG0991, BG1112, BG1190, BG1228). Cost is priced over the whole window and for long Grok prompts (BG1279, BG1305, BG1330, BG1331), but every lane this run was multi-unit and lane return cannot split one builder's total, so per-unit cost stays unpriced (BG1397). BG1420, added when the push gate found five red tests, fixed them but was carried as BG1425 after its repair's round-2 review.

> **Run:** 2026-11-12T21:23:26Z to 2026-11-13T03:48:46Z (6.4h)
> **Verified on:** ec57e17d73f497699c8ce4c198e74e26a27ef294   **Fingerprint:** 82ced251b004932d

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes over the units' own measured minutes, summed over the units that also
carry a forecast; tokens over the whole run. The run's wall-clock span stands on its own
line with no ratio. Ratio is actual over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 49 | 49 | 1.0x | 24 of 24 delivered unit(s) |
| Minutes | 286.2 | 2464.2 | 8.61x | measured active minutes (spans or agent minutes) against their forecast, over the 24 of 24 unit(s) planned or added and not dropped that carry both |
| Wall-clock span | not forecast | 385.3 | no ratio | the run's minutes, start to end, so waiting counts; the forecast is active work, so the two are not compared |
| Priced cost | not forecast | 41,431,558 | no ratio | priced input-equivalent tokens, the run's headline cost, each component times its weight: input + output + cache write 6,286,357 (input 3,946 x1, output 1,749,423 x5, cache write 5m 4,252,006 x1.25, cache write 1h 280,982 x2, cache read 268,035,252 x0.1); the sum is the Tokens row; read from the main thread and every subagent transcript, once per message |
| Tokens | 9,126,348 | 6,286,357 | 0.69x | the whole run: forecast over 24 of 24 unit(s) planned or added and not dropped; actual is the run meter, which reads the main thread and every subagent transcript, so the subagents are already in the reading and the 2 delegated total(s) supplied are not added |
| Priced per point | not forecast | 845,542 | no ratio | the Priced cost row over the 49 point(s) of the 24 delivered unit(s), in priced input-equivalent tokens per point |
| Dollar cost | not forecast | $111.66 | no ratio | estimated US dollars: each model's own components in the Priced cost row times that model's list prices; price table effective 2026-11-12; covers 100.0% of the priced tokens |
| Dollars per point | not forecast | $2.28 | no ratio | the Dollar cost row over the 49 point(s) of the 24 delivered unit(s); price table effective 2026-11-12 |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. The
actual on the Minutes row above sums these minutes over the units that also carry a forecast;
spans of units open at the same time overlap, so that sum can exceed the wall-clock span.

| Unit | Dollars | Forecast minutes | Minutes | Forecast tokens | Tokens | Priced |
| --- | --- | --- | --- | --- | --- | --- |
| BG1190 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 20.1 | 372,504 | 1,407,336 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1190 --agent A` |
| BG1228 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 20.1 | 372,504 | 1,414,113 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1228 --agent A` |
| BG1112 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 54.2 | 186,252 | 1,883,907 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1112 --agent A` |
| BG1005 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 200.2 | 372,504 | 4,922,737 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1005 --agent A` |
| BG1009 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 199.8 | 558,756 | 4,913,269 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1009 --agent A` |
| BG0991 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 157.9 | 372,504 | 4,146,387 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG0991 --agent A` |
| BG1336 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 142.4 | 372,504 | 3,830,116 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1336 --agent A` |
| BG1337 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 142.4 | 372,504 | 3,830,116 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1337 --agent A` |
| BG1339 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 61.6 | 372,504 | 1,187,895 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1339 --agent A` |
| BG1344 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 61.6 | 372,504 | 1,194,181 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1344 --agent A` |
| BG1330 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 142.4 | 558,756 | 3,830,116 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1330 --agent A` |
| BG1279 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 183.8 | 372,504 | 4,553,754 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1279 --agent A` |
| BG1331 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 184.4 | 558,756 | 4,625,355 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1331 --agent A` |
| BG1305 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 106.6 | 372,504 | 3,200,533 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1305 --agent A` |
| BG1371 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 61.6 | 186,252 | 2,278,773 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1371 --agent A` |
| BG0965 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 61.6 | 372,504 | 2,278,773 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG0965 --agent A` |
| BG1340 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 86.0 | 372,504 | 2,788,021 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1340 --agent A` |
| BG1341 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 86.0 | 186,252 | 2,788,021 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1341 --agent A` |
| BG0990 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 86.0 | 372,504 | 2,788,021 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG0990 --agent A` |
| BG1343 | NOT MEASURED - no agent returned for it was priced from its own transcript | 5.8 | 86.0 | 186,252 | 2,788,021 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1343 --agent A` |
| BG1333 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 61.6 | 558,756 | 2,278,773 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1333 --agent A` |
| BG1261 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 97.8 | 372,504 | 1,930,866 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1261 --agent A` |
| BG1262 | NOT MEASURED - no agent returned for it was priced from its own transcript | 17.5 | 97.7 | 558,756 | 1,930,866 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1262 --agent A` |
| BG1372 | NOT MEASURED - no agent returned for it was priced from its own transcript | 11.7 | 62.1 | 372,504 | 1,003,458 | NOT MEASURED - no agent returned for it was priced from its own transcript - price one with `sprint.py lane return --units BG1372 --agent A` |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 24 | 49 |
| Delivered of the plan | 24 | 49 |
| Added mid-run and delivered | 0 of 1 added | 0 |
| Dropped | 1 | 3 |
| Carried undelivered | 0 | 0 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 49.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG1190 | 2 | 2 | delivered | 2 |
| BG1228 | 2 | 2 | delivered | 1 |
| BG1112 | 1 | 1 | delivered | 1 |
| BG1005 | 2 | 2 | delivered | 2 |
| BG1009 | 3 | 3 | delivered | 2 |
| BG0991 | 2 | 2 | delivered | 1 |
| BG1336 | 2 | 2 | delivered | 1 |
| BG1337 | 2 | 2 | delivered | 1 |
| BG1339 | 2 | 2 | delivered | 1 |
| BG1344 | 2 | 2 | delivered | 1 |
| BG1330 | 3 | 3 | delivered | 1 |
| BG1279 | 2 | 2 | delivered | 2 |
| BG1331 | 3 | 3 | delivered | 2 |
| BG1305 | 2 | 2 | delivered | 1 |
| BG1371 | 1 | 1 | delivered | 1 |
| BG0965 | 2 | 2 | delivered | 1 |
| BG1340 | 2 | 2 | delivered | 1 |
| BG1341 | 1 | 1 | delivered | 1 |
| BG0990 | 2 | 2 | delivered | 1 |
| BG1343 | 1 | 1 | delivered | 1 |
| BG1333 | 3 | 3 | delivered | 1 |
| BG1261 | 2 | 2 | delivered | 1 |
| BG1262 | 3 | 3 | delivered | 1 |
| BG1372 | 2 | 2 | delivered | 1 |
| BG1420 | 3 | 3 | dropped - carried at the review cap: BG1425 | 2 |

## Known issues handed over

42 open finding(s) raised in the run, 25 close gap(s), 0 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG1420 | High | Run eleven's lanes turn the full suite red in five tests the per-commit runs never selected |
| BG1391 | Medium | The report's Dollar cost row does not carry the lower-bound label for a Grok figure priced from a session total, so a lower bound reads as exact - not-stop-ship, ruled by orchestrator |
| BG1393 | Medium | A project that replaces grok-4.7 under pricing.models loses grok-4.7@long-context from its own table, so run_state.usd prices only part of the reading - not-stop-ship, ruled by orchestrator |
| BG1394 | Medium | A re-close after a reopen whose meter cannot be read drops the first window, takes no reading and says nothing on the page - not-stop-ship, ruled by orchestrator |
| BG1395 | Medium | BG1005 makes a criterion whose pytest target partly skips on the running machine read red, including Done criteria the release gate re-runs, and the count is not measured - not-stop-ship, ruled by orchestrator |
| BG1396 | Medium | A Verify line with its own -q makes pytest run at -qq with no summary, so a partial skip is stamped pass, and -s and an unpinned _PYTEST_SKIP_NODE add edge cases - not-stop-ship, ruled by orchestrator |
| BG1397 | Medium | sprint lane return --agent refuses a multi-unit lane, so a multi-unit lane's builder is never priced per unit - not-stop-ship, ruled by orchestrator |
| BG1399 | Medium | lane land commits and lands the code, then refuses a self-check missing a required surface, when the builder can no longer be resumed - not-stop-ship, ruled by orchestrator |
| BG1400 | Medium | lane accept takes --reviewer as free text, so a carried unit's re-review under the wrong id strands an APPROVE that only an operator supersession retires - not-stop-ship, ruled by orchestrator |
| BG1406 | Medium | lane run accepts a home-isolated unit and hands its worktree builder the main-checkout brief, and 'Isolation: no home' reads as home - not-stop-ship, ruled by orchestrator |
| BG1407 | Medium | A builder's mutation probe in a scratch copy of the tests runs without the repo-root conftest.py, so without HOME confinement - not-stop-ship, ruled by orchestrator |
| BG1409 | Medium | lane land's rebase uses --empty=keep --reapply-cherry-picks, so a commit a builder made that main already holds becomes an empty commit - not-stop-ship, ruled by orchestrator |
| BG1413 | Medium | A Ctrl-C during lane run's 2 s kill grace drops the SIGKILL that follows, so a SIGTERM-ignoring child stages after the run, and nothing pins that SIGKILL - not-stop-ship, ruled by orchestrator |
| BG1417 | Medium | CI's lint.yml sets up Node 20 while markdownlint-cli and markdownlint declare node >=22, so the gap is invisible until a dependency uses a Node 22 API - not-stop-ship, ruled by orchestrator |
| BG1425 | Medium | BG1420 did not converge in review: round 2 REJECT findings - not-stop-ship, ruled by orchestrator |
| BG1382 | Low | A nested run_verifier caller's own verifier can outlive it, because both levels wait the same one second grace and Ctrl-C leaks the inner verifier - not-stop-ship, ruled by orchestrator |
| BG1383 | Low | Two more group-kill helpers duplicate verify_ac's, one closure in mutation.py and one in verify_ac._run_phase - not-stop-ship, ruled by orchestrator |
| BG1384 | Low | The changelog's 6.3.0 text and the BG1112 fragment still over-state what the group kill does - not-stop-ship, ruled by orchestrator |
| BG1385 | Low | This repo's own AGENTS.md lacks the template's 'Integrate continuously' line, so validate.py check warns here - not-stop-ship, ruled by orchestrator |
| BG1386 | Low | Timing tests fail under parallel load: test_status GatherPerformanceTests read 4.9 s against a 3 s limit and a verify_ac criterion failed once at load 8.6 - not-stop-ship, ruled by orchestrator |
| BG1387 | Low | test_cli_grammar RealTreeMarkerTests copies the whole tree into /tmp and fails with EDQUOT on a small tmpfs - not-stop-ship, ruled by orchestrator |
| BG1388 | Low | An sdlc_md root-discovery test fails when TMPDIR is inside a repository, because it assumes its temporary directory lies outside any project - not-stop-ship, ruled by orchestrator |
| BG1389 | Low | sdlc_md.extract_field reads an empty field on into the next line and returns '>', and two is_swallowed_run branches are unpinned - not-stop-ship, ruled by orchestrator |
| BG1390 | Low | test_lean_tracked_run_record test_this_repos_signed_reports_check_in_a_clean_clone fails in a harness worktree - not-stop-ship, ruled by orchestrator |
| BG1392 | Low | prices and token_meters have untested edges: `_rates()` falls back to an empty table, `_list`'s long-context pop, a true threshold read as 1, and `book()` splits labelled lower bound - not-stop-ship, ruled by orchestrator |
| BG1398 | Low | The tool-call budget in a multi-unit lane brief is printed once per unit and nothing states the lane's total - not-stop-ship, ruled by orchestrator |
| BG1401 | Low | BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test - not-stop-ship, ruled by orchestrator |
| BG1402 | Low | The BG1333 integration rule counts as present if 'Integrate continuously' appears anywhere in AGENTS.md, so a sentence negating it passes - not-stop-ship, ruled by orchestrator |
| BG1403 | Low | retro's new `supplied` guard and its `declined` list have no tests - not-stop-ship, ruled by orchestrator |
| BG1404 | Low | critic.py record splits a verdict's ISSUES at every semicolon, so a semicolon inside one finding becomes an untagged finding and the record is refused - not-stop-ship, ruled by orchestrator |
| BG1405 | Low | Nothing pins critic's 'live rows' filter, the carried-refusal wording or the stacked-criterion naming, and the BG1339 rejoinder path guards are untested - not-stop-ship, ruled by orchestrator |
| BG1408 | Low | sprint lane land's hook-refusal text and module docstring say the worktree and main are as they were, which is untrue after the replay, and _discard_own_artefacts is untested - not-stop-ship, ruled by orchestrator |
| BG1410 | Low | BG1330's re-pointed clean-run test lost its known-issues assertion, unpriced_units' filter is untested, and lane land with no run open names lane return's --tokens flag - not-stop-ship, ruled by orchestrator |
| BG1411 | Low | The unpriced-gap remedy 'lane return --units <id> --agent A' cannot work after the close - not-stop-ship, ruled by orchestrator |
| BG1412 | Low | templates/agents/sdlc-builder.md and its pinned .claude/agents copy still tell a builder to run verify_ac without --dry-run - not-stop-ship, ruled by orchestrator |
| BG1414 | Low | The BG1262/BG1261 changelog headline is too broad, the help line reads as SIGTERM-first for every death of sprint.py, and lanes._reaping sends SIGKILL first - not-stop-ship, ruled by orchestrator |
| BG1415 | Low | No test pins the line number verify_ac's lint prints - not-stop-ship, ruled by orchestrator |
| BG1416 | Low | help/verify.md's exit-3 row in the revert-check table leaves out git failing to read the base blob - not-stop-ship, ruled by orchestrator |
| BG1421 | Low | verify_ac's revert check reads a missing runner binary as red rather than as no verdict - not-stop-ship, ruled by orchestrator |
| BG1422 | Low | No test pins verify_ac's class and module skip-mark check on the decorator's name - not-stop-ship, ruled by orchestrator |
| BG1423 | Low | file_finding writes a title with bare underscores into the bug heading and index, which markdownlint then refuses as emphasis - not-stop-ship, ruled by orchestrator |
| BG1424 | Low | A bare sprint close runs its whole pre-flight report before scaffolding the retro, so the scaffold takes many minutes - not-stop-ship, ruled by orchestrator |
| checklist | close gap | known-issues: Known issues carried, each with its stop-ship ruling - 1 unruled, 0 malformed row(s) |
| unpriced | close gap | BG1190: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1190 --agent A` |
| unpriced | close gap | BG1228: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1228 --agent A` |
| unpriced | close gap | BG1112: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1112 --agent A` |
| unpriced | close gap | BG1005: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1005 --agent A` |
| unpriced | close gap | BG1009: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1009 --agent A` |
| unpriced | close gap | BG0991: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0991 --agent A` |
| unpriced | close gap | BG1336: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1336 --agent A` |
| unpriced | close gap | BG1337: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1337 --agent A` |
| unpriced | close gap | BG1339: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1339 --agent A` |
| unpriced | close gap | BG1344: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1344 --agent A` |
| unpriced | close gap | BG1330: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1330 --agent A` |
| unpriced | close gap | BG1279: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1279 --agent A` |
| unpriced | close gap | BG1331: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1331 --agent A` |
| unpriced | close gap | BG1305: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1305 --agent A` |
| unpriced | close gap | BG1371: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1371 --agent A` |
| unpriced | close gap | BG0965: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0965 --agent A` |
| unpriced | close gap | BG1340: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1340 --agent A` |
| unpriced | close gap | BG1341: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1341 --agent A` |
| unpriced | close gap | BG0990: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG0990 --agent A` |
| unpriced | close gap | BG1343: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1343 --agent A` |
| unpriced | close gap | BG1333: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1333 --agent A` |
| unpriced | close gap | BG1261: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1261 --agent A` |
| unpriced | close gap | BG1262: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1262 --agent A` |
| unpriced | close gap | BG1372: its cost is NOT MEASURED - no agent returned for it was priced from its own transcript; price one with `sprint.py lane return --units BG1372 --agent A` |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M78TKD.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 6,286,357 |

Total 6,286,357, of which delegated 325,321. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

**Prices.** Each model the Dollar cost row priced, at the prices this page was filed with (its
own price table), in US dollars per million tokens, beside that model's dollars.

| Model | Input | Output | Cache write 5m | Cache write 1h | Cache read | Effective | Source | Dollars |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-opus-5-5 | $4.00 | $20.00 | $5.00 | $8.00 | $0.20 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $111.20 |
| claude-sonnet-5-5 | $2.00 | $10.00 | $2.50 | $4.00 | $0.10 | 2026-11-06 | <https://platform.claude.com/docs/en/about-claude/pricing> (Model pricing table, read 2026-11-06) | $0.4591 |

**Cost by role.** The session's spend by role, each cell as `sprint cost --anatomy` prints it,
from acd73b30-154a-4170-83eb-043073708d4b, 516 subagent transcript(s); total agents 25, calls 1,905, priced 41,431,558. Priced in input-equivalent tokens; split is each
part's share of the role's priced cost; context is input + cache write + cache read per call.

| Role | Agents | Calls | Priced tokens | Share | Cache read | Cache write | Output | First context | Avg context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 1 | 269 | 10,574,313 | 25.5% | 87.7% | 5.3% | 6.9% | 197,959 | 345,932 |
| builder | 1 | 60 | 805,770 | 1.9% | 48.9% | 17.6% | 33.6% | 14,060 | 67,504 |
| reviewer | 0 | 0 | 0 | 0.0% | not available | not available | not available | not available | not available |
| repair | 1 | 39 | 691,119 | 1.7% | 39.9% | 18.0% | 42.0% | 13,753 | 73,340 |
| other | 22 | 1,537 | 29,360,356 | 70.9% | 57.4% | 17.2% | 25.4% | 14,391 | 112,301 |

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 21 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; with no forge run data a deployment is counted as a commit on main inside the run window | on demand | git history - 21 commit(s) on main inside the run window |
| Lead time for changes | 5h 51m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 21 commit(s) |
| Change failure rate | NOT MEASURED - no forge run data | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that concluded failure or timed out - a cancelled or skipped run is not a failed deployment | 0-15% | no push-triggered CI run is readable for this run window |
| Time to restore | NOT MEASURED - no forge run data | per red streak on main, in creation order, the span from its first failure's conclusion to the conclusion of the first push-triggered run created after it that concluded success, floored at zero; the median over the window's restored streaks, or not restored while the window's last streak is still red | under an hour | no push-triggered CI run is readable for this run window |

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

4 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. The tally is this clone's refusal log as the close read it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 1 | 0 | 1 | delete candidate: 8 refusal(s) over 3 runs and no candidate catch |
| markdown | 3 | 0 | 3 | delete candidate: 8 refusal(s) over 3 runs and no candidate catch |

### Lessons

6 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-015 | a retirement outruns the deletion | graduating (CR0684) | 0 | 3 |
| LC-017 | a page-format rule mark nothing round-trips | graduating (CR0664) | 0 | 3 |
| LC-018 | a doc claim checked by reading | graduating (CR0643) | 0 | 30 |
| LC-019 | a push-gate guard the per-commit run skips | active | 0 | 0 |
| LC-020 | git and harness state a test leaks | active | 0 | 0 |
| LC-021 | lane paperwork the landing refuses | active | 0 | 0 |
