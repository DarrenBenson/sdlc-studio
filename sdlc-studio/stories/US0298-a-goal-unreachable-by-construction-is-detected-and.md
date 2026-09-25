# US0298: A goal unreachable by construction is detected and named at plan time

> **Status:** Done
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
- **Verify:** manual - retired by US0916: `review.two_role_after` and the reachable-end-state cap it drove were deleted, so no batch is capped short of Done; the plan reaching Done past a legacy cutoff is test_lean_no_two_role.py::TwoRoleGoneTests::test_the_plan_reaches_done
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

### AC2: a batch the gate does not reach still reaches Done

- **Given** a batch with no `review.two_role_after` configured, or every unit at or below the
  cutoff
- **When** `sprint plan` runs
- **Then** the reachable end state is Done and no unreachability is reported, so the check
  cannot become a warning that always fires
- **Verify:** manual - retired by US0916: `review.two_role_after` and the reachable-end-state cap it drove were deleted, so no batch is capped short of Done; the plan reaching Done past a legacy cutoff is test_lean_no_two_role.py::TwoRoleGoneTests::test_the_plan_reaches_done
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

### AC3: the finding is recorded, not only printed

- **Given** `sprint plan --write` over a batch whose reachable end state is short of Done
- **When** the run is opened
- **Then** the reachable end state and its reason sit on the run state beside the Sprint Goal,
  so the closing `goal-verdict` cites the constraint that was known at plan time instead of
  re-deriving it
- **Verify:** manual - retired by US0916: `review.two_role_after` and the reachable-end-state cap it drove were deleted, so no batch is capped short of Done; the plan reaching Done past a legacy cutoff is test_lean_no_two_role.py::TwoRoleGoneTests::test_the_plan_reaches_done
- **Verified:** manual (2026-09-25) - retired, superseded by US0916

## Open Questions

- [x] CR0354 asks for "a goal that no seat can judge achievable" to be reported, which is a seat -- NOT ANSWERED; owned by BG0421 (the delivery made a choice, nobody recorded whether it was the right one)
  judgement, while "unreachable by construction" is mechanical. This story specifies only the
  mechanical half: the derived reachable end state. Whether the goal's own prose is then
  compared against it mechanically, or left to the seat consult in US0297, is unstated -
  Owner: operator
- [x] Which other gates feed the derivation is unstated. Only the two-role rule is named in -- NOT ANSWERED; owned by BG0421 (the delivery made a choice, nobody recorded whether it was the right one)
  CR0354; `require_ac_verification` and the AC-verify Done gate could also cap the reachable
  state - Owner: implementer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and ACs authored against CR0354 |
| 2026-09-25 | US0916 | AC1-AC3 retired in the D0259 pattern: `review.two_role_after` and the reachable-end-state cap it drove were deleted with the per-unit sign-off, and their three `test_sprint.py` tests with them |
