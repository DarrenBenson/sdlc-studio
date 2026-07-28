# US0501: A close retry over an unchanged test-relevant surface reuses the previous gate verdict instead of re-running it

> **Status:** Review
> **Delivers:** CR0454
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator retrying a close
**I want** a retry over an unchanged surface to reuse the previous gate verdict
**So that** four attempts at a close cost one gate run, not four

## Acceptance Criteria

### AC1: a retry over an unchanged surface does not re-run the gate

- **Given** a close that ran the gate, and a retry whose test-relevant surface is unchanged
- **When** the close is retried
- **Then** it reuses the recorded verdict and says so, instead of paying the full cost again
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRetryTests::test_a_retry_over_an_unchanged_surface_reuses_the_verdict

### AC2: a retry after a real change re-runs it

- **Given** a retry whose surface changed
- **When** the close is retried
- **Then** the gate runs again, so the reuse can never mask work done between attempts
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRetryTests::test_a_retry_after_a_change_reruns_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
