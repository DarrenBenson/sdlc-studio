# US0599: A panel may sign a unit only when every adversarial verdict on it carries brief provenance, and missing provenance STOPS the run and notifies rather than parking it

> **Status:** Ready
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

### AC2: missing provenance STOPS and notifies rather than parking the unit

- **Given** the refusal above
- **When** it fires during an unattended run
- **Then** the run stops and reports it as a TOOLING failure needing attention, rather than leaving the unit at Review for a human to discover, because a machine that cannot proceed says so immediately
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelInterlockTests::test_missing_provenance_stops_and_notifies

### AC3: a fully briefed unit signs without complaint

- **Given** a unit whose adversarial verdicts all carry provenance
- **When** the panel signs
- **Then** it succeeds, so the interlock cannot be satisfied by one that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PanelInterlockTests::test_a_briefed_unit_signs_cleanly

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
