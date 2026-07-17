# US0198: sprint close orchestrates goal-verdict, retro validate and extract, close gate, handoff and reconcile with fail-loud stops and idempotent resume, printing the decision brief

> **Status:** Review
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0068
> **Points:** 5

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the twelve-step sprint close sequenced by one deterministic command that refuses at each gate
**So that** no close step is a skippable seam, and the reviewer-of-record ask always arrives with its composed brief

## Acceptance Criteria

### AC1: the chain runs in order, stops loudly, resumes idempotently

- **Given** a run with a written retro and a step primed to fail mid-chain
- **When** `sprint close --retro RETROxxxx` runs, and re-runs after the repair
- **Then** sprint close runs the chain in order and STOPS loudly at the first failing gate, naming the remedy; a re-run after repair resumes idempotently
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint.py -k CloseChain
- **Verified:** yes (2026-07-16)

### AC2: the decision brief is composed, not hand-written

- **Given** a completed run with critic verdicts, gate and mutation results and a recorded forecast
- **When** the close chain reaches its final step
- **Then** The printed decision brief carries per-unit deliveries, each unit's verdict + reject history from critic-verdicts.md, gate and mutation results, and forecast vs measured subagent spend - the CR0318 content, composed not hand-written
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint.py -k CloseBrief
- **Verified:** yes (2026-07-16)

### AC3: absent judgement inputs are refusals, never defaults

- **Given** a run missing retro content, an unset goal, or an unjudged goal-verdict
- **When** `sprint close` runs
- **Then** Nothing is invented: absent retro content, an unset goal, or an unjudged goal-verdict are refusals with the command to run, never defaults
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_sprint.py -k CloseRefus
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
