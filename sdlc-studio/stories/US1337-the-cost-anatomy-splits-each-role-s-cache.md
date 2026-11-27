# US1337: The cost anatomy splits each role's cache writes into growth and re-writes after the cache lifetime

> **Status:** Done
> **Depends on:** BG1764, US1332
> **Risk-class:** elevated
> **Delivers:** RFC0069
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy_rewrites.py, changelog.d/US1337.md
> **Epic:** EP0383
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for what each team's delivery costs (Abena)
**I want** the cost anatomy to split each role's cache writes into growth and re-writes after the cache lifetime
**So that** I can tell how much of a role's cache spend bought new context and how much paid again for context that expired while it waited

Each role row of the anatomy gains its cache writes split into growth, re-written after 5-minute expiry and re-written after 1-hour expiry, and `sprint cost --anatomy` prints the split per role in text and JSON. Lifetimes come from the write kind each usage record carries: `cache_creation.ephemeral_5m_input_tokens` lives 5 minutes and `ephemeral_1h_input_tokens` 1 hour; a write the split does not account for is already booked at 5 minutes, so it takes the 5-minute lifetime. Within one transcript a call's gap is the time since the previous call's first usage record. Its 5-minute writes are a re-write when the gap is longer than 5 minutes, its 1-hour writes when longer than 60; otherwise, and for a transcript's first call, they are growth.

## Acceptance Criteria

### AC1: a 5-minute write after a gap longer than 5 minutes is a re-write

- **Given** a session whose one subagent writes 5-minute cache of 3,000, 400, 400 and 4,000 tokens at minutes 1, 2, 3 and 9, and a second fixture whose gap is exactly 5 minutes
- **When** `sprint.py cost --anatomy --session --transcripts <dir> --format json` runs
- **Then** that subagent's role carries 3,800 growth and 4,000 re-written after 5-minute expiry, and the exactly-5-minute gap counts as growth. Fails on: HEAD, whose role rows carry no split at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy_rewrites.py::CacheRewriteTests::test_a_five_minute_write_after_a_longer_gap_is_a_rewrite
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint.py cost --anatomy` (`cmd_cost`)

### AC2: the lifetime comes from the write kind

- **Given** a main thread writing 1-hour cache of 2,000, 500 and 9,000 tokens at minutes 0, 6 and 67
- **When** the anatomy is read
- **Then** the orchestrator carries 2,500 growth and 9,000 re-written after 1-hour expiry: the 6-minute gap that makes a 5-minute write a re-write in AC1 is growth here. Fails on: HEAD, which has no split; one lifetime for both kinds would also fail it, by booking the 500 as a re-write
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy_rewrites.py::CacheRewriteTests::test_the_lifetime_comes_from_the_write_kind
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint.py cost --anatomy` (`cmd_cost`)

### AC3: a call inside the run's window measures its gap from the call before it

- **Given** an open run whose window starts between a subagent's call at minute 1 and its next call at minute 9, the second writing 4,000 tokens of 5-minute cache
- **When** the anatomy is read over the open run's window
- **Then** that write counts as re-written after expiry, measured from the minute-1 call outside the window, and the minute-1 call's own write is not counted. Fails on: HEAD, which has no split; a gap taken from the window's first call would also fail it, by booking the write as growth
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy_rewrites.py::CacheRewriteTests::test_a_window_call_measures_its_gap_from_the_call_before_it
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint.py cost --anatomy` over an open run, and `stamp_cost_roles` in `lib/run_state.py`, which reads the anatomy over the run's window at the close

### AC4: the printed split adds up, and a missing timestamp reads not available

- **Given** the AC1 and AC2 session, and a subagent one of whose usage records carries no timestamp
- **When** `sprint.py cost --anatomy --session` runs in text and in JSON
- **Then** each role's growth plus its re-writes equals its `cache_write_5m` plus `cache_write_1h` components, the text prints the three figures per role, and the role holding the untimed record reads `not available` for its split, never 0. Fails on: HEAD, which prints no split; its text table's columns end at avg context
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy_rewrites.py::CacheRewriteTests::test_the_printed_split_adds_up_and_an_untimed_record_reads_not_available
- **Verified:** yes (2026-11-26)
- **Caller:** `sprint.py cost --anatomy` (`cmd_cost`)

## Notes

- Depends on BG1764 (both edit `lib/cost_anatomy.py`) and US1332 (both edit `reference-sprint.md`).
- A post-expiry call's whole write counts as re-write: the transcript cannot separate its new turn from the prefix written again, so the figure overstates the re-write by one turn. `reference-sprint.md#cost-anatomy` says so and documents both lifetimes.
- Compute gaps over the whole transcript (`whole` in `build`) and sum only the calls the window keeps, as the start context is read whatever the window.
- This session's own transcripts show why the split matters: the main thread writes 1-hour cache and each subagent writes 5-minute cache, so a builder's or reviewer's long wait loses its cache while the orchestrator's survives.
- How the fixture proves each case: the 6-minute gap appears on both write kinds, a re-write on the subagent's 5-minute write (AC1) and growth on the main thread's 1-hour write (AC2), which shows the lifetime comes from the write kind and not from one constant; the exactly-5-minute gap pins the boundary as growth; the window case (AC3) pins the gap to the previous call, not to the window's first.
- The RFC's options B to D wait for this measurement (D0637); none is drafted here.
- `test_cost_anatomy.py` runs 12 tests in 8.96 s; a new module of four stays well inside 120 s.
- Grounded at HEAD db54c42bb on 2026-11-26, with a fixture of a main transcript writing 1-hour cache of 2,000, 500 and 9,000 tokens at minutes 0, 6 and 67 and one subagent writing 5-minute cache of 3,000, 400, 400 and 4,000 at minutes 1, 2, 3 and 9: `sprint.py cost --anatomy --session --transcripts <tx> --root <fx> --format json` exited 0; every role row's keys were agent_ids, agents, avg_context, calls, components, first_context, priced, role, share and split; the orchestrator's components held `cache_write_1h 11500` and the subagent role's `cache_write_5m 7800`; the text table's columns end at avg context. No row carries a growth or re-write figure.
- Lifetimes: this session's main transcript records read `"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":876` and a subagent's `"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":8444`, each with an ISO timestamp.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | engineering seat | Groomed for run twenty-eight from the D0635 breakdown |
