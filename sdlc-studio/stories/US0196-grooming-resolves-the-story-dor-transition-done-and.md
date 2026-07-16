# US0196: grooming resolves the story DoR; transition Done and the critic gate resolve the story DoD; gate require-retro and release resolve the sprint and release DoD; absent documents stay byte-compatible with today

> **Status:** Ready
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/conformance.py
> **Epic:** EP0066
> **Points:** 5

## User Story

**As** Jonah Reyes (team lead)
**I want** the existing gates to read the ready and done bars from the project's DoR/DoD documents
**So that** editing a criterion changes what is enforced, and an unenforced DoD stops being skippable prose

## Acceptance Criteria

### AC1: each gate resolves its level from the documents, defaults byte-compatible

- **Given** a project with tailored DoR/DoD documents and a project with none
- **When** sprint plan grooming, transition to Done, the critic gate, gate --require-retro and gate --release each run
- **Then** Each named gate resolves its level's tagged criteria from the project documents; absent documents = shipped-default behaviour, byte-compatible with today
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_dor_dod.py -k GateResolve

### AC2: a document edit changes gate behaviour; removing a tag downgrades visibly

- **Given** a project document whose tagged criterion is edited, and one whose tag is removed
- **When** the affected gate re-runs
- **Then** A project edit to a tagged criterion changes gate behaviour without code changes; an edit that removes a tag downgrades that criterion to human-judged visibly in gate output
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_dor_dod.py -k TagEdit

### AC3: the close clause restates the close-down enforcement without regression

- **Given** the existing close-down enforcement suite
- **When** the sprint-DoD close clause replaces the hardcoded close-down check
- **Then** RFC0042's close-down enforcement is restated as the sprint-DoD close clause with no behavioural regression (existing close tests stay green)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_close_guard.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
