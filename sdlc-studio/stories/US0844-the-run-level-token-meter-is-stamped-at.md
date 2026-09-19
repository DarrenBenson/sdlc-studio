# US0844: the run-level token meter is stamped at run open and at report time, and the total names the sessions it covers

> **Status:** Done
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0255
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, reading the cost row of her own run's report
**I want** the run's token total stamped at open and at report time, and labelled with the sessions it covers
**So that** the report's headline cost is a measurement rather than the word UNMEASURED that every unit of RUN-01M2JA6J carried

## Acceptance Criteria

How attribution works today, because the fix is a change to it rather than a new mechanism.
`run_state.open_run` stamps `TOKEN_BASELINE` once, on a fresh run only, from
`run_state.session_tokens` - the transcript's summed input, output and cache-creation tokens,
cache reads excluded. At the close, `retro.run_attributed_tokens` subtracts that baseline from
the current reading. It returns NOT ATTRIBUTABLE, deliberately and correctly, when
`base["source"] != cap["source"]` - the baseline was taken in a different session from the one
closing the run, so the two readings are of different meters and their difference is not a
spend. That guard is the reason RUN-01M2JA6J's every unit reads `UNMEASURED (no telemetry token
record)` and its sprint total reads `not attributable`: the run was CLOSED ACROSS SESSIONS,
which is the normal shape of a long run, not an error.

RFC0059 states in its own text that a report printing unknown in its headline row every run is
worse than no report, and D3 ruled the attribution RUN-LEVEL: per-unit actuals stay UNMEASURED
and are named, because the meter is cumulative per session and interleaved work cannot be split
between units honestly. So the fix is to stop taking ONE reading and start taking a stamp per
session, making the run total the sum of per-session deltas - which is a spend, each term being
a difference of two readings of the same meter - and to label it with the sessions it covers,
because an unqualified total over a partially stamped run is a partial one.

The figures below are RUN-01M2JA6J's own, measured this way after the fact: 6,459,675 tokens
over 103 points, 62,715 per point. Fixtures drive `session_tokens` through the transcripts
directory (`SDLC_STUDIO_TRANSCRIPTS`), as `test_retro.py`'s harness-capture fixtures already do.

### AC1: the meter is stamped at run open and again at report time, each stamp naming its session

- **Given** a fresh run opened against a transcript `s1.jsonl` whose usage records sum to 4,271,975, the transcript then grown so it sums to 10,731,650
- **When** the run is opened, and PREPARE later builds the report in that same session
- **Then** the run record carries an ORDERED list of stamps rather than one baseline, each holding the reading, its transcript path, an ISO time and a kind - the first `open`, the last `report`; the `open` stamp still reads 4,271,975, unchanged by the second; and `run_state.run_token_total(state)` returns 6,459,675 with one session named
- **Mutant:** overwrite the single `TOKEN_BASELINE` at report time instead of appending a stamp - the delta is then zero and the run reports no cost at all, while a test that only checks a stamp exists still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PrepareAndSealTests::test_prepare_takes_the_report_time_stamp_through_the_shipped_lane
- **Verified:** yes (2026-09-18)

### AC2: a run spanning sessions sums its per-session deltas and names the sessions it covers

- **Given** a run opened in session `s1` (stamped at 4,271,975, that transcript reaching 10,731,650) and prepared in session `s2`, whose own transcript reads 120,000 when the run first writes to it and 900,000 at report time, with a stamp taken at each of those four moments
- **When** `run_state.run_token_total(state)` is called
- **Then** it returns 7,239,675 - the sum of the two same-session deltas, 6,459,675 and 780,000 - names both transcript paths and the session count 2, and labels the figure a LOWER BOUND; it is not `not attributable`, which is what a single cross-session baseline produces today and what RUN-01M2JA6J's close printed
- **Mutant:** keep `run_attributed_tokens`' rule that a baseline taken in another session makes the whole run not attributable - the headline cost row is then UNMEASURED on every run closed across sessions, which is the run this story was raised from, and every single-session test still passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RunTokenStampTests::test_a_run_spanning_sessions_sums_its_stamps_and_names_them
- **Verified:** yes (2026-09-18)

### AC3: the report's cost row prints the total, the model, the rate and the coverage, and NOT MEASURED only when no stamp can be read

- **Given** AC2's run, its batch summing 103 points; and a second copy whose transcripts directory holds no session file at all
- **When** PREPARE builds the report on each
- **Then** the first copy's cost row carries the total, the model the stamps recorded, the per-point figure derived from total and points, and a coverage clause naming the session count and any session that wrote to the run without a stamp; the second reads `NOT MEASURED` with the reason `session_tokens` returned, never `0` and never a per-point figure of zero; in both, every per-unit token actual reads UNMEASURED by name, under D3
- **Mutant:** print the run total with no coverage clause - a partial total then reads as the run's cost, which is the consult's finding that an unqualified total over a run closed across sessions is a partial one; OR fall back to a zero total instead of NOT MEASURED when no stamp is readable, which is the criterion's second half and was declared by the Then clause with no mutant naming it; must redden on both
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ReportCostRowTests::test_the_cost_row_names_its_total_model_rate_and_session_coverage
- **Verified:** yes (2026-09-18)

### AC4: a run carrying only the legacy single baseline still reports, and says which shape it read

- **Given** a run state holding the pre-change `session_token_baseline` dict alone - the shape every run open at delivery time carries, including the one this story ships in
- **When** the report's cost row is produced
- **Then** it reads the legacy baseline, states the figure it can derive from it, and names the shape it read, so an older run is reported rather than refused
- **Mutant:** require the stamp list - every run opened before this story lands then reports NOT MEASURED, including the run that delivers it, which is the fixture-green-is-not-target-green scar this project already carries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CostRowTests::test_a_legacy_single_baseline_is_read_and_named
- **Verified:** yes (2026-09-18)

### AC5: a run that opened before the open stamp existed prices itself from its opening reading, not from its stamped window

- **Given** a run state holding BOTH the legacy `session_token_baseline` and stamps taken later in that same session - the shape of every run already open when AC1's `open_run` stamp lands, which has no `open` stamp and can never acquire one
- **When** the run's token total is taken
- **Then** the baseline is read as a reading of that session's meter and enters its delta, so the figure spans the run rather than the gap between whichever stamps exist; a baseline naming a transcript the stamps do not is left out, because the difference of two meters is not a spend
- **Mutant:** prefer the stamp list and drop the baseline whenever any stamp exists - RUN-01M2SPNS, whose PREPARE stamped twice, then prices 9.6 hours of work at the 44 minutes between them and publishes it as a measurement, because every other clause of the cost row is true
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RunTokenStampTests::test_a_legacy_baseline_earlier_than_the_stamps_is_part_of_the_delta
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | `run_state`: overwrite the single `TOKEN_BASELINE` at report time instead of appending a stamp - the delta is then zero and the run reports no cost, while a test that only checks a stamp exists still passes | the meter is stamped at run open and again at report time, each stamp naming its session |
| AC2 | `run_state.run_token_total`: keep `run_attributed_tokens`' rule that a baseline taken in another session makes the whole run not attributable - the headline cost is then UNMEASURED on every run closed across sessions, and every single-session test still passes | a run spanning sessions sums its per-session deltas and names the sessions it covers |
| AC3 | `sprint_report._cost_section`: drop the uncovered-sessions clause from the coverage figure; ALSO fall back to a zero total instead of NOT MEASURED when no stamp is readable - must redden on both | the report's cost row prints the total, the model, the rate and the coverage, and NOT MEASURED only when no stamp can be read |
| AC4 | `sprint_report._cost_section`: require the stamp list, so every run opened before this story lands reports NOT MEASURED, including the run that delivers it | a run carrying only the legacy single baseline still reports, and says which shape it read |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: three criteria, and the user story filled. Written against why RUN-01M2JA6J read `not attributable`: `run_attributed_tokens` refuses a baseline taken in another session, and that run was closed across sessions. One stamp per session replaces the single baseline, the total is the sum of same-session deltas and names its coverage. Figures are the run's own, 6,459,675 over 103 points. test_run_state.py added to Affects. |
| 2026-09-18 | goal review round 5 | AC4 added for the LEGACY single `session_token_baseline` shape - the state every run open at delivery time carries, including the one this story ships in. Without it the cost row reads NOT MEASURED on its own run, which is this project's fixture-green scar. |
| 2026-09-18 | delivery | AC3's second mutant named, and a second Verify line for it. The Then clause already required "never `0` and never a per-point figure of zero", and no declared mutant could falsify it - one criterion's words outrunning its fixture, which is this repo's dominant review defect. Both mutants were applied and killed. AC3's Verify also now drives PREPARE through `sprint.py`, not the composer's function: the Given says "when PREPARE builds the report", and a library call cannot see the wiring that files the report and stamps the run state. |
| 2026-09-18 | plan review round 1 | AC1's Verify moved from the library call to the LANE. Its When names PREPARE building the report, and `stamp_tokens` had shipped with a test as its only caller - so the criterion's own verifier could not see that no second stamp was ever taken, and `test_run_state.py` stayed green while every run reported its cost as zero. The selector now drives `sprint.py`'s `_file_the_report` and asserts the stamp shape the Then describes; the library test remains as supporting evidence, bound to nothing. |
| 2026-09-18 | CLI exercise | AC5 added. The filed report priced RUN-01M2SPNS at 90,809 main-thread tokens against a real cost near 3M, because this run opened BEFORE AC1's `open` stamp existed: its opening reading sits in the legacy `session_token_baseline` and `run_token_total` ignored the baseline outright whenever any stamp was present, so the total spanned the two PREPARE stamps rather than the run. AC4 covers a baseline ALONE; nothing covered a baseline beside a partial stamp list, which is the state every run open when AC1 landed occupies permanently. Found by reading the filed page, not by the suite. |
