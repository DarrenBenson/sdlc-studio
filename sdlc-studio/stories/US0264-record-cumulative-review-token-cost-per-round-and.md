# US0264: Record cumulative review token cost per round and show it when the next round is offered

> **Status:** Ready
> **Delivers:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Epic:** EP0085
> **Points:** 3

## User Story

**As an** operator being offered another review round
**I want** to see what the rounds so far have actually cost
**So that** "is the next round worth buying" is a question asked against a number rather than a feeling

## Acceptance Criteria

### AC1: Each round records its own token cost

- **Given** a completed review round with a known token cost
- **When** the round is recorded
- **Then** that cost is stored against the round on the run state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_round_records_its_token_cost

### AC2: The cumulative total is shown when the next round is offered

- **Given** two recorded rounds costing 80k and 60k
- **When** a third round is offered
- **Then** the offer states the per-round costs and the cumulative 140k
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_next_round_offer_shows_cumulative_cost

### AC3: An unmeasured round says so and is never counted as zero

- **Given** a round whose token cost could not be measured
- **When** the cumulative total is rendered
- **Then** the round is shown as unmeasured and the total is marked as a partial sum - an unmeasured round is never silently added as 0, which would understate the spend
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_unmeasured_round_is_named_not_zeroed

### AC4: A recorded cost survives a re-record and an explicit zero can still clear it

- **Given** a round with a recorded cost
- **When** the round is re-recorded without a cost
- **Then** the recorded value is reused, not erased; and an explicit zero is distinguishable from absent, so it can still clear the value deliberately
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_recorded_cost_survives_rerecord_and_explicit_zero_clears

## Notes

AC4 is the direct lesson of L-0156 and BG0224: an upsert told not to overwrite must
**reuse** the recorded value rather than omit it, and `if not cost` treats a real 0 as
absent. Both defects have shipped on this codebase already - test the zero case
explicitly, not just the happy path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: user story and ACs authored; the zero/unmeasured cases pinned from L-0156 and BG0224 |
