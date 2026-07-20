# US0264: Record cumulative review token cost per round and show it when the next round is offered

> **Status:** Done
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
- **Verified:** yes (2026-07-20)

### AC2: The cumulative total is shown when the next round is offered

- **Given** two recorded rounds costing 80k and 60k
- **When** a third round is offered
- **Then** the offer states the per-round costs and the cumulative 140k
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_next_round_offer_shows_cumulative_cost
- **Verified:** yes (2026-07-20)

### AC3: An unmeasured round says so and is never counted as zero

- **Given** a round whose token cost could not be measured
- **When** the cumulative total is rendered
- **Then** the round is shown as unmeasured and the total is marked as a partial sum - an unmeasured round is never silently added as 0, which would understate the spend
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_unmeasured_round_is_named_not_zeroed
- **Verified:** yes (2026-07-20)

### AC4: A measured zero is distinguishable from an unmeasured round

- **Given** a round whose measured cost was zero
- **When** the cost report is rendered
- **Then** it reads as a measured zero, not as unmeasured, and the total is not marked partial - the two are different facts and neither is inferred from falsiness
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_a_measured_zero_is_not_unmeasured
- **Verified:** yes (2026-07-20)

## Notes

AC3 and AC4 carry the lesson of L-0156 and BG0224 into this surface: `if not cost` treats a
real 0 as absent, and an unmeasured round summed as zero understates a total the operator is
meant to weigh a purchase against. Both defects have shipped on this codebase already, so the
zero case is pinned explicitly rather than only the happy path.

The preservation half of that lesson (an upsert told not to overwrite must reuse the recorded
value) does **not** apply here, which AC4 originally assumed: rounds are append-only, so no
round is ever re-recorded. What survives is the distinction the lesson rests on - measured
zero and unmeasured are different facts, and neither may be inferred from falsiness.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: user story and ACs authored; the zero/unmeasured cases pinned from L-0156 and BG0224 |
| 2026-07-20 | sdlc-studio | AC4 corrected at verification: it assumed upsert semantics (a round re-recorded without a cost reusing the value), but rounds are append-only, so no re-record exists to test. Rewritten to the property actually delivered - a measured zero is not an unmeasured round - rather than repointing the Verify line at a passing test |
