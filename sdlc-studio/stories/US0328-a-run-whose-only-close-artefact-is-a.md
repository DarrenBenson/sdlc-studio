# US0328: A run whose only close artefact is a FAILED close attempt is open-and-protected, not absorbable

> **Status:** Review
> **Delivers:** CR0401
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Epic:** EP0111
> **Points:** 3

## User Story

**As an** operator whose last close attempt failed and left work outstanding
**I want** that run treated as open and protected rather than absorbable
**So that** the next batch I plan does not vanish into the run I was in the middle of
closing, which is the run most likely to be worked around

## Acceptance Criteria

### AC1: a recorded failed close attempt does not make a run absorbable

- **Given** a run with `outcome` `running`, one `close_attempts` entry recording nine
  items outstanding, and none of `sprint_goal_verdict`, `ended_at` or `handoff`
- **When** a disjoint batch is planned against it with `--write`
- **Then** the plan is refused and the run's batch is exactly the batch it held before,
  so the mid-close run is covered by the guard rather than exempt from it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::FailedCloseAttemptIsProtectedTests::test_a_run_with_only_a_failed_close_attempt_refuses_a_disjoint_batch
- **Verified:** yes (2026-07-23)

### AC2: protected is not finished, so a truly closed run is still replaced

- **Given** two runs judged in turn, one carrying only a failed close attempt and one
  carrying `ended_at`
- **When** a disjoint batch is planned against each
- **Then** the first is refused with its id, batch and close attempts intact, and the
  second is archived and replaced by a fresh run at exit zero, so `close_attempts` never
  becomes a close artefact and never silently discards a run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::FailedCloseAttemptIsProtectedTests::test_close_attempts_protect_the_run_while_ended_at_still_replaces_it
- **Verified:** yes (2026-07-23)

### AC3: the refusal says the run is mid-close and how much it left outstanding

- **Given** the run whose single close attempt left nine items outstanding
- **When** the plan is refused
- **Then** the refusal states that a close attempt has already run against that run and
  names the outstanding count it left, so the operator is pointed at finishing the close
  rather than at abandoning the run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::FailedCloseAttemptIsProtectedTests::test_refusal_names_the_failed_close_attempt_and_its_outstanding_count
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
