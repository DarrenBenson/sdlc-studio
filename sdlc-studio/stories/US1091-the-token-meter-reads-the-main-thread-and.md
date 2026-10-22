# US1091: The token meter reads the main thread and every subagent transcript once per message, prices each component from one weight table, and the close and the report state that priced cost as their headline

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1091.md
> **Epic:** EP0292
> **Points:** 5
> **Depends on:** BG1111
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, paying for every sprint the skill runs on her behalf
**I want** the run's cost read from the main thread and every subagent the run started, each component (input, output, cache write at 5 minutes and at 1 hour, cache read) stated on its own and priced input-equivalent from one weight table
**So that** I see what the run really cost, and where, instead of a main-thread figure that omits the reviewers, the builders and the cache reads that are most of the bill

## Acceptance Criteria

- **AC1:** Given a fixture transcript directory holding a main-thread transcript and two subagent transcripts under `<session-id>/subagents/agent-*.jsonl` (one of them a depth-2 agent, which the harness writes into the same flat directory), each repeating one message's usage on three records, when `run_state.session_tokens` reads it, then the reading carries each component (input, output, cache write 5m from `cache_creation.ephemeral_5m_input_tokens`, cache write 1h from `ephemeral_1h_input_tokens`, cache read) summed once per `message.id`, split into main thread and subagents, and `tokens` is input + output + cache write over both
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::MeterComponentsTests::test_main_and_subagent_components_are_counted_once_per_message
- **AC2:** Given the same fixture, the reading's `priced` figure equals each component times its weight in `TOKEN_WEIGHTS` (input 1, cache write 5m 1.25, cache write 1h 2.0, cache read 0.1, output 5) and moves when a weight is changed in-process; the close's and the report's headline cost is `priced`, labelled as priced input-equivalent tokens, with the input + output + cache-write sum listed beside it as a component (D0390)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::MeterPricedTests::test_priced_reads_the_weight_table_and_is_the_headline
- **AC3:** Given an open run, when two meter stamps are taken either side of a subagent's completion, then `run_token_total` reports the priced delta and each component's delta beside `tokens`; given a run whose stamps were written before this change (no priced figure), `priced` is None with a reason naming the legacy stamps, never 0, and `tokens` is unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::MeterStampsTests::test_the_run_total_carries_priced_deltas_and_names_legacy_stamps
- **AC4:** Given a run whose stamps say the reading includes subagent transcripts and a builder total supplied with `sprint.py lane return --units <id> --tokens N`, when the run's actual is formed for the report (`sprint_report._run_tokens_actual`) and the retro (`retro.run_attributed_tokens`), then N is not added and the basis says the subagents are already in the reading; given a run whose stamps carry no such flag, as every run before this change, N is still added, so an earlier signed page re-derives unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py::MeterDelegatedTests::test_a_supplied_total_is_not_added_over_a_reading_that_holds_subagents

## Notes

- Serves: Maya Okafor, End goal 3.
- The open stamp taken on an earlier basis is US1097 (split out: at 8 points this story tripped the backlog's oversized lens, which US0854 AC1 holds the push to).
- AC1 must fail on: the subagents directory not read; 1h writes folded into 5m; a subagent's repeated records counted per record (BG1111's defect reintroduced on the new path); subagent records dropped by the cwd check, since a worktree agent records the worktree as its cwd
- AC2 must fail on: weights typed beside the sum rather than read from the table; one weight for both cache-write durations; the headline left as the unpriced sum (D0346 (1), superseded by D0390)
- AC3 must fail on: `priced` defaulting to 0 for a legacy stamp; `priced` derived from `tokens` times a constant rather than from the stamped components
- AC4 must fail on: delegated totals added unconditionally, which counts every builder and reviewer twice; delegated totals suppressed for every run, which moves the figure on pages already signed
- The headline change is D0390 (1). US1092 carries the VELOCITY and forecast half (D0390, split for size).
- Overlap: id: BG1111; relation: prerequisite, its own unit delivered first (D0389); evidence: Proposed Fix: 'Count each assistant message once, keyed on `message.id`'. E1 extends the same reader to the subagent files and assumes the de-duplication is in place.
- Overlap: id: US0991; relation: partly superseded for the Claude reader: E1 AC4 delivers its AC1 and AC2; its AC3 and AC4 (a non-Claude harness's basis on the report) remain; evidence: AC1: 'Given a reading whose basis says it includes subagent spend and a supplied delegated total on the run, when `run_attributed_tokens` forms the run's figure, then the delegated total is not added'
- Overlap: id: US0986; relation: regroom after E1: its AC1 pins today's figure, which E1 changes; its AC4 matches E1's design; evidence: AC1: 'the reading equals today's `session_tokens` figure for that transcript (input + output + cache creation, cache reads excluded, the main-thread basis)'; AC4: 'carry cache reads as a separate figure outside `tokens` (D0346)'
- Overlap: id: US0999; relation: narrowed: for Claude subagents the model is read from each transcript's `message.model`, so the supplied-model path matters only for agents outside the harness's store; evidence: AC1: 'a builder's total is returned with `sprint lane return --units <unit> --tokens 120000 --model claude-sonnet-4-6`'
- Overlap: id: US1000; relation: complementary (6.3, D0388): money per model can be computed from E1's stamped components rather than one blended token count; evidence: Title: 'The cost section states the run's cost in money from a pricing snapshot frozen at the close'
- Overlap: id: EP0276; relation: parent of US1000; related, not superseded; evidence: Title: 'The report of record is reviewable from the committed tree and states its cost in money'
- Overlap: id: CR0611; relation: shares D0346's basis; the other harness readers report `priced` as None until each states its cache split; evidence: D0346 (1): 'one counting basis for every harness reader - input + output + cache write in the headline, cache reads recorded separately and excluded'
- Overlap: id: BG0252; relation: Fixed by stating the lower bound; E1 removes the bound for Claude, so the 'LOWER BOUND' basis sentence in `session_tokens` and `TOKEN_TOTAL_BASIS` changes; evidence: Title: 'The harness token capture counts only the main thread, so a fan-out sprint publishes roughly a third of what it actually cost'
- Risk: The weights given for the measurement (cache write 1.25) price only 5-minute writes. In this project's transcripts the main thread writes the 1-hour cache only (session acd73b30: 16.6M 1h, 0 5m) and subagents the 5-minute cache only (32.7M 5m, 0 1h). A 1h write is 2.0x input, so the 74.5M and 78.2M figures understate the main thread's writes by about 6% on this session's numbers.
- Risk: The headline basis changes twice in one run (BG1111's de-duplication, then subagents). Rows on three bases would pool into one tokens-per-point rate unless the Source column tells them apart, which AC5 requires.
- Risk: The transcript layout is the harness's, not this project's, and is undocumented. A missing or reshaped subagents directory must read as a named failure or a main-thread-only basis, never as zero subagent spend.
- Risk: `_records_cwd` must not be applied to subagent files: worktree agents record `.claude/worktrees/agent-*` as their cwd (5 of 81 subagent files here).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-22 | sdlc | AC5: an open stamp on an earlier counting basis is re-derived from the transcript, never subtracted across bases (BG1111 builder's finding: RUN-01M5EM9N's open stamp) |
| 2026-10-22 | sdlc | Points 5 -> 8 for AC5's re-derivation of an earlier-basis open stamp |
| 2026-10-22 | sdlc | AC5 split out to US1097; Points 8 -> 5 (the oversized lens holds the push via US0854 AC1) |
