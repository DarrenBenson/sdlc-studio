# US0502: The doctrine names the silent-stall failure mode and gives a driving agent a detection rule it can apply

> **Status:** Ready
> **Delivers:** CR0450
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/../reference-agentic-lessons.md, .claude/skills/sdlc-studio/scripts/../reference-audit.md
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** agent driving delegated work
**I want** the doctrine to name the silent-stall failure mode and give me a rule for detecting it
**So that** I stop waiting on a delegate that will never answer, instead of treating silence as progress

## Acceptance Criteria

### AC1: the doctrine names the failure mode and its detection

- **Given** the agentic-execution reference
- **When** it is read
- **Then** it states that a delegate can stop without erroring, that an absent result must never be read as pending, and how a driver tells one from the other
- **Verify:** pytest tools/tests/test_doc_claims.py::StallDoctrineTests::test_the_stall_mode_and_detection_are_documented

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
