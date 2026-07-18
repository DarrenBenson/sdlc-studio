# US0236: sprint close --apply-signoff records per-unit sign-off and Done transitions, refusing without an explicit principal

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Epic:** EP0077
> **Points:** 5

## User Story

**As an** operator closing a sprint
**I want** one command to fan my recorded approval into per-unit sign-offs and Done transitions
**So that** I approve once as the reviewer of record instead of hand-running `critic.py signoff` and `transition` for every unit in the batch

## Acceptance Criteria

### AC1: `--apply-signoff` refuses without an explicit principal

- **Given** an open run whose close chain has passed
- **When** `sprint close --retro <id> --apply-signoff` runs with no `--principal`
- **Then** it exits non-zero, records no sign-off, and names that the reviewer of record must be given explicitly
- **Verify:** grep "apply-signoff needs an explicit --principal" .claude/skills/sdlc-studio/scripts/sprint.py
- **Verified:** yes (2026-07-18)

### AC2: with a principal it records a sign-off and transitions each story unit Done

- **Given** a batch of story units held at Review, each with recorded critic evidence and an APPROVE verdict
- **When** `sprint close --retro <id> --apply-signoff --principal "<name>"` runs
- **Then** each story unit gets a reviewer-of-record sign-off (author != principal) and is transitioned Done; bugs already terminal are left untouched
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.ApplySignoffTests
- **Verified:** yes (2026-07-18)

### AC3: a subagent principal is refused, and the fan stops loudly at the first refusal

- **Given** a principal that is an authoring-session subagent (a recorded reviewer on a unit), or a unit whose Done gate is red
- **When** `--apply-signoff` reaches it
- **Then** it stops non-zero at that unit naming the refusal, leaving already-signed-and-done units done (no partial-silent state)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.ApplySignoffStopsTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
