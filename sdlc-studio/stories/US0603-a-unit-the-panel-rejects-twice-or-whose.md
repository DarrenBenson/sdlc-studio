# US0603: A unit the panel rejects twice, or whose seats disagree, escalates to the operator by NOTIFYING rather than waiting

> **Status:** Done
> **Closed with findings in:** repaired in 307ce91d - panel_escalation is called from review-batch
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
- **Verified:** yes (2026-08-02)

### AC2: disagreeing seats escalate rather than auto-resolve

- **Given** a panel whose seats return different verdicts
- **When** the result is read
- **Then** it escalates with the disagreement named, and is never resolved by majority silently, because the disagreement is the signal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_disagreeing_seats_escalate
- **Verified:** yes (2026-08-02)

### AC3: escalation NOTIFIES rather than waits

- **Given** an escalation during an unattended run
- **When** it fires
- **Then** the reason states the operator is notified and nothing waits on a reply, because an escalation that blocks on input that will not arrive is indistinguishable from a hang
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_escalation_notifies_rather_than_waits
- **Verified:** yes (2026-08-02)

### AC4: a single rejection does not escalate

- **Given** one REJECT on a unit
- **When** the rule runs
- **Then** it does not escalate, because a first REJECT is the loop working and escalating on it would fire on every ordinary finding until the operator stopped reading the channel
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_one_rejection_does_not_escalate
- **Verified:** yes (2026-08-02)

### AC5: a unanimous panel does not escalate

- **Given** a panel whose seats all returned the same verdict
- **When** the rule runs
- **Then** it does not escalate, so the rule cannot be satisfied by one that escalates everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EscalationTests::test_a_unanimous_panel_does_not_escalate
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
