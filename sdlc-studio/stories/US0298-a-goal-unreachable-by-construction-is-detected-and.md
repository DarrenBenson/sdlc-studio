# US0298: A goal unreachable by construction is detected and named at plan time

> **Status:** Draft
> **Delivers:** CR0354
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0098
> **Points:** 3

## User Story

**As a** sprint operator
**I want** the plan to derive the furthest state this batch can actually reach under the gates
that apply to it, and to say so plainly when that state is short of Done
**So that** a goal nothing could have satisfied is caught before the work rather than recorded
as partial at the close

## Acceptance Criteria

### AC1: the reachable end state is derived from the gates that reach the batch

- **Given** a project with `review.two_role_after: 192` and a batch of stories numbered above
  that cutoff, where Done needs an independent reviewer-of-record sign-off the authoring
  session is refused
- **When** `sprint plan` runs
- **Then** the plan names the reachable end state as Review rather than Done, gives the two-role
  rule as the reason, and names the units the rule reaches
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_plan_names_the_reachable_end_state_under_the_two_role_gate
- **Verified:** yes (2026-07-22)

### AC2: a batch the gate does not reach still reaches Done

- **Given** a batch with no `review.two_role_after` configured, or every unit at or below the
  cutoff
- **When** `sprint plan` runs
- **Then** the reachable end state is Done and no unreachability is reported, so the check
  cannot become a warning that always fires
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_a_batch_the_two_role_gate_does_not_reach_can_still_reach_done
- **Verified:** yes (2026-07-22)

### AC3: the finding is recorded, not only printed

- **Given** `sprint plan --write` over a batch whose reachable end state is short of Done
- **When** the run is opened
- **Then** the reachable end state and its reason sit on the run state beside the Sprint Goal,
  so the closing `goal-verdict` cites the constraint that was known at plan time instead of
  re-deriving it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_the_reachable_end_state_is_recorded_on_the_run_state
- **Verified:** yes (2026-07-22)

## Open Questions

- [ ] CR0354 asks for "a goal that no seat can judge achievable" to be reported, which is a seat
  judgement, while "unreachable by construction" is mechanical. This story specifies only the
  mechanical half: the derived reachable end state. Whether the goal's own prose is then
  compared against it mechanically, or left to the seat consult in US0297, is unstated -
  Owner: operator
- [ ] Which other gates feed the derivation is unstated. Only the two-role rule is named in
  CR0354; `require_ac_verification` and the AC-verify Done gate could also cap the reachable
  state - Owner: implementer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and ACs authored against CR0354 |
