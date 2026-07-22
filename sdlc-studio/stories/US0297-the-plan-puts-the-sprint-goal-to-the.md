# US0297: The plan puts the Sprint Goal to the resolved seats and records achievability and definition of done

> **Status:** Draft
> **Delivers:** CR0354
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0098
> **Points:** 5

## User Story

**As a** sprint operator approving a batch at the triage STOP
**I want** the review seats to judge the Sprint Goal itself - is it achievable by this batch,
what does done mean for it, does the batch hang together as one increment - before the plan
is written
**So that** I approve a batch against a goal somebody has examined, instead of paying for a
wrong goal at the close

## Acceptance Criteria

### AC1: the plan carries a seat verdict on the goal, not only WSJF scores

- **Given** a batch with a stated Sprint Goal and the review seats resolved
- **When** `sprint plan` runs
- **Then** the plan records, per consulted seat, its achievability verdict, what done means for
  the goal, and whether the batch reads as one increment - alongside the WSJF components, never
  in place of them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_plan_records_a_seat_verdict_on_the_sprint_goal
- **Verified:** yes (2026-07-22)

### AC2: the verdict is stamped on the run state at plan time

- **Given** `sprint plan --write` over a reviewed goal
- **When** the run is opened
- **Then** the seat verdict sits on the run state next to `sprint_goal`, carrying its date and
  the seats that gave it, so the closing `goal-verdict` judges the goal against what the seats
  said then rather than against a later reconstruction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_goal_review_is_stamped_on_the_run_state_at_plan_time
- **Verified:** yes (2026-07-22)

### AC3: an unreviewed goal blocks the plan

- **Given** a stated Sprint Goal that no seat has reviewed
- **When** `sprint plan --write` runs without `--skip-personas`
- **Then** it exits non-zero, writes no `sprint-plan.json`, opens no run, and names the command
  that records the seat review
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_plan_refuses_a_sprint_goal_no_seat_has_reviewed
- **Verified:** yes (2026-07-22)

### AC4: `--skip-personas` stays the recorded escape

- **Given** a stated Sprint Goal and `--skip-personas`
- **When** the plan runs
- **Then** the plan is written and the run opened, and both the printed plan and the run state
  say the goal went unreviewed, so the close can see it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_skip_personas_records_the_goal_as_unreviewed
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0354 does not say how a seat verdict reaches the planner: a `.local/` inputs file in the
  shape of `wsjf-inputs.json`, a `sprint.py` subcommand, or a flag. The ACs are written against
  the recorded verdict, whichever surface writes it - Owner: implementer
- [ ] CR0354 does not say whether a plan with NO Sprint Goal stated is also refused. AC3 fires
  only on a stated goal; a goalless plan keeps today's behaviour - Owner: operator
- [ ] Whether the seat verdict rots on a clock the way `wsjf-inputs.json` does (advisory 7-day
  window, warn only) is unstated - Owner: operator

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and ACs authored against CR0354 |
