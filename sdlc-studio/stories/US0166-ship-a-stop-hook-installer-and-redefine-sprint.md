# US0166: Ship a Stop-hook close guard and redefine sprint-done as close-gate-green

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/hooks/close_guard.py
> **Epic:** EP0046
> **Points:** 5

## User Story

**As an** agent that could stop a turn with a close still owed
**I want** the harness to remind me at the moment I would stop
**So that** the Definition of Done's close clause is enforced by the harness, not my recall

## Acceptance Criteria

### AC1: the Stop hook blocks a turn end when a close is owed and allows it otherwise

- **Given** a baselined project with an owed close
- **When** the `close_guard.py` Stop hook evaluates the turn-end event
- **Then** it returns a `block` decision naming the owed units; a covered, unbaselined, or
  already-blocked (`stop_hook_active`) turn is allowed
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_close_guard.py
- **Verified:** yes (2026-07-16)

### AC2: default-allow on the hook's own bug - a parse error never blocks a turn

- **Given** empty or malformed stdin
- **When** the hook reads the event
- **Then** it parses to an empty event and never blocks on that error (it falls back to the process
  cwd; if that tree genuinely owes a close it may block - that is the feature, not a bug)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_close_guard.py
- **Verified:** yes (2026-07-16)

### AC3: the doctrine records that a sprint is done only when the close gate is green, never at "deployed"

- **Given** the close-down doctrine
- **When** `reference-retro.md` and `help/gate.md` are read
- **Then** both state the Definition-of-Done close clause and the `--require-close` / Stop-hook enforcement
- **Verify:** grep -q "never at .deployed" .claude/skills/sdlc-studio/help/gate.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
