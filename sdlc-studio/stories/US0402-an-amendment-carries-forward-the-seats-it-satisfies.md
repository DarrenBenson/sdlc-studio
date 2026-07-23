# US0402: an amendment carries forward the seats it satisfies and re-consults only the rest, recording the prior wording and the requesting seat

> **Status:** Done
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0408
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0152
> **Points:** 5

## User Story

**As a** lead running the Sprint Goal review before a run
**I want** to amend the goal to do exactly what a seat asked, carrying that seat's verdict forward and re-consulting only the seats the change does not satisfy
**So that** improving a goal in the direction a review requested costs the seats it touches, not a full fresh round

## Acceptance Criteria

### AC1: An amendment carries the satisfied seat's verdict forward to the new wording

- **Given** a recorded review of goal A in which engineering asked for a reframed wording
- **When** the goal is amended to goal B, declaring engineering the requesting seat
- **Then** a new round is recorded against goal B carrying engineering's verdict, so planning goal B is discharged for that seat without consulting it again
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AmendGoalReviewTests::test_amendment_carries_forward_the_satisfied_seats_verdict
- **Verified:** yes (2026-07-23)

### AC2: The amendment records the previous wording and the requesting seat

- **Given** goal A is amended to goal B at engineering's request
- **When** the amend round is written
- **Then** the round records the prior wording (goal A) and the requesting seat (engineering), so the trail shows the goal was improved rather than replaced
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AmendGoalReviewTests::test_the_amend_round_records_prior_wording_and_requesting_seat
- **Verified:** yes (2026-07-23)

### AC3: Seats the amendment does not satisfy are flagged for re-consult

- **Given** goal A reviewed by product, engineering and qa, then amended to goal B satisfying only engineering
- **When** the amended review's status is read
- **Then** product and qa are reported as needing a fresh verdict against goal B while engineering is not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AmendGoalReviewTests::test_seats_not_satisfied_by_the_amendment_still_need_reconsult
- **Verified:** yes (2026-07-23)

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code. Mutation-proven by hand: dropping the amendment carry-forward, letting a material change carry, inverting the needs-reconsult set, not storing the brief in the round, and ignoring the fields-file seats were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built and mutation-proven |
