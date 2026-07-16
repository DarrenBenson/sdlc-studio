# US0189: critic brief assembles the seat-review prompt; critic record --from-verdict parses the returned block, refusing malformed input

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0059
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the critic ceremony's scaffolding emitted and parsed deterministically
**So that** every seat review starts from the same complete brief and every verdict lands in the record unmangled

## Acceptance Criteria

### AC1: brief assembles the review prompt

- **Given** a unit with ACs and Affects and a named seat
- **When** critic.py brief --unit USxxxx --seat qa runs
- **Then** the printed brief carries the seat charter reference, the ACs, the Affects-derived diff scope and the exact VERDICT/ISSUES/BLOCKING return contract; unknown unit or seat refused
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k Brief

### AC2: record parses the verdict block

- **Given** a returned VERDICT/ISSUES/BLOCKING block on stdin or file
- **When** critic.py record --from-verdict runs
- **Then** the verdict is recorded with reviewer/author/tier; a malformed or verdict-less block is refused loudly
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k FromVerdict

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
