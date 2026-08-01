# US0603: A unit the panel rejects twice, or whose seats disagree, escalates to the operator by NOTIFYING rather than waiting

> **Status:** Ready
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0198
> **Points:** 5

## User Story

**As a** operator who is informed rather than involved
**I want** a disagreeing or twice-rejecting panel escalated to me by notification
**So that** a stuck unit reaches me immediately instead of waiting silently

## Acceptance Criteria

### AC1: a twice-rejected unit escalates

- **Given** a unit the panel has rejected twice
- **When** the loop next runs
- **Then** it escalates to the operator rather than attempting a third round
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_a_twice_rejected_unit_escalates

### AC2: disagreeing seats escalate rather than auto-resolve

- **Given** a panel whose seats return different verdicts
- **When** the result is read
- **Then** it escalates with the disagreement named, and is never resolved by majority silently, because the disagreement is the signal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_disagreeing_seats_escalate

### AC3: escalation NOTIFIES rather than waits

- **Given** an escalation during an unattended run
- **When** it fires
- **Then** the run reports it immediately and stops, rather than blocking on input that will not arrive
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_escalation_notifies_rather_than_waits

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
