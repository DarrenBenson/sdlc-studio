# US0427: a subagent reviewer of record in its own context is accepted, and the row records that it was a delegated agent

> **Status:** Done
> **Delivers:** RFC0051
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0159
> **Points:** 5

## User Story

**As an** operator delegating a sign-off
**I want** a subagent reviewer of record in its own context accepted, with the row recording that it was a delegated agent
**So that** the authorised delegation is usable and the record carries what produced the verdict

## Acceptance Criteria

### AC1: a subagent reviewer of record in its own context is accepted

- **Given** a sign-off whose reviewer of record is a subagent running in a separate context
- **When** `record_signoff` is called
- **Then** it is accepted and the row records that the reviewer was a DELEGATED AGENT - D0059 authorises this deliberately, and the record must carry what produced the verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffDelegateTests::test_authoring_session_subagent_is_accepted_as_a_DISCLOSED_delegate
- **Verified:** yes (2026-07-26)

### AC2: the delegation is never silent

- **Given** the same sign-off
- **When** the verdict rows are read back
- **Then** the delegated marker is present and cannot be omitted - the whole trade D0059 makes is disclosure in place of independence, so a delegated sign-off that reads as an ordinary one destroys the only thing the decision bought
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffDelegateTests::test_verdict_reviewer_is_accepted_as_a_DISCLOSED_delegate
- **Verified:** yes (2026-07-26)

### AC3: an author signing their own work is still refused

- **Given** a sign-off whose principal is the unit's own author
- **When** it is recorded
- **Then** it is REFUSED - D0059 widens who may act as reviewer of record, and does not touch the self-approval guard
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SignoffDelegateTests::test_self_signoff_refused
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
