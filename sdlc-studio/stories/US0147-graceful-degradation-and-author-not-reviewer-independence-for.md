# US0147: Graceful degradation and author-not-reviewer independence for the consult

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_resolve.py
> **Epic:** EP0040
> **Points:** 3

## User Story

**As an** operator on any project
**I want** the consult to degrade gracefully and stay independent
**So that** it works with no seats, fails loud on a broken seat, and never self-signs-off.

## Acceptance Criteria

### AC1: no seats → shipped defaults; broken project seat → fail before minting; skip-personas bypasses; independence floor holds

- **Given** a project with no seats, a broken project seat, or `--skip-personas`
- **When** refine/triage resolve the consult
- **Then** no seats falls back to the shipped defaults; a project seat missing its review render raises before anything is minted (fail-empty); `--skip-personas` bypasses even a broken seat; and the seat framing carries the "separate instance / never sign off your own work" independence floor
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_amigo_consult.DegradationIndependenceTests
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
