# US0599: A panel may sign a unit only when every adversarial verdict on it carries brief provenance, and missing provenance STOPS the run and notifies rather than parking it

> **Status:** Review
> **Delivers:** CR0514
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0198
> **Points:** 5

## User Story

**As a** maintainer relying on a panel verdict
**I want** a panel blocked from signing until every adversarial verdict on the unit carries brief provenance
**So that** a panel cannot ratify a review nobody can prove was properly briefed

## Acceptance Criteria

### AC1: an unbriefed adversarial verdict blocks the panel

- **Given** a unit whose adversarial verdicts include one with no brief fingerprint
- **When** the panel attempts to sign
- **Then** it is refused naming that verdict, because a panel ratifying an unbriefed review launders the missing provenance rather than catching it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelInterlockTests::test_an_unbriefed_verdict_blocks_the_panel
- **Verified:** yes (2026-08-01)

### AC2: the interlock binds the PANEL, never the operator

- **Given** a unit whose adversarial verdict carries no provenance
- **When** the operator signs it directly rather than a panel
- **Then** it is recorded, because a human principal reads the evidence themselves and can see it is unbriefed - blocking them would withhold exactly the units most worth their attention, which is the opposite of human-in-the-lead
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelInterlockTests::test_an_operator_signoff_is_not_subject_to_the_interlock
- **Verified:** yes (2026-08-01)

> The run-stopping half of CR0514's interlock clause - halting an unattended run and notifying
> rather than parking the unit - is delivered by US0603, where escalation lives. This unit
> supplies the refusal and states it is a TOOLING failure rather than a judgement call, which
> is what tells the loop it may not simply retry.

### AC3: a fully briefed unit signs without complaint

- **Given** a unit whose adversarial verdicts all carry provenance
- **When** the panel signs
- **Then** it succeeds, so the interlock cannot be satisfied by one that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelInterlockTests::test_a_briefed_unit_signs_cleanly
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
