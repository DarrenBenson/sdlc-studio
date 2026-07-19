# US0256: census the CR-index Linked Epics column from Decomposed-into (or drop the dead column)

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0082
> **Points:** 3

## User Story

**As a** reader of the CR index
**I want** the Linked Epics column derived from the CR files' Decomposed-into headers
**So that** the index stops asserting that no CR ever spawned an epic

## Acceptance Criteria

### AC1: reconcile detects an unpopulated Linked Epics cell as drift

- **Given** a CR file carrying `> **Decomposed-into:** EPxxxx` whose index row reads `--`
- **When** `reconcile.py detect` runs
- **Then** it reports the cell as drift, naming the CR and the epic the file claims
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_reconcile.py -k LinkedEpicsCensusTests
- **Verified:** yes (2026-07-19)

### AC2: reconcile apply syncs the column from the files

- **Given** the same workspace with the drift detected
- **When** `reconcile.py apply` runs
- **Then** each row's Linked Epics cell carries the epic ids from its file, a CR with no Decomposed-into keeps `--`, and a second pass reports clean
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_reconcile.py -k LinkedEpicsApplyTests
- **Verified:** yes (2026-07-19)

### AC3: A new decomposition writes the column at source

- **Given** a CR with no epic yet
- **When** `refine` decomposes it into an epic
- **Then** the index row's Linked Epics cell is written with the new epic id in the same operation, so reconcile finds no drift immediately after
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_two_backlogs.py -k RefineLinkedEpicsColumnTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
