# US0500: An artefact the close itself creates does not count as an unreviewed change against that same close

> **Status:** Review
> **Delivers:** CR0454
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator watching a close refuse itself
**I want** an artefact the close creates not to count as an unreviewed change against that same close
**So that** recording the close does not invalidate it, and filing an honest finding during it is not punished with another full gate

## Acceptance Criteria

### AC1: the close's own output does not fail its own review lane

- **Given** a close that writes the review anchor and the handoff
- **When** the same close re-checks review currency
- **Then** those artefacts are recognised as its own output and do not make the review stale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseSelfInvalidationTests::test_the_close_output_does_not_fail_its_own_review_lane

### AC2: a finding filed during the close is carried, not treated as unreviewed work

- **Given** a finding filed while the close runs
- **When** the close continues
- **Then** it is recorded as carried into the next run rather than failing the current one, so honest filing is not punished
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseSelfInvalidationTests::test_a_finding_filed_during_the_close_is_carried

### AC3: a real blocker in the work still refuses

- **Given** a genuine correctness failure in a batch unit
- **When** the close runs
- **Then** it still refuses, and its message distinguishes a blocker in the work from one the close created itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseSelfInvalidationTests::test_a_real_blocker_still_refuses_and_is_named_as_such

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
