# US0255: extend the write-confinement snapshot suite across the shipped writers with a roster sweep

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Epic:** EP0082
> **Points:** 5

## User Story

**As a** maintainer trusting the TSD's integration target
**I want** every shipped writer held to a before/after write-confinement snapshot
**So that** a script that writes outside its named target is caught by the suite, not by a corrupted workspace

## Acceptance Criteria

### AC1: The major writers carry confinement snapshots

- **Given** the confinement suite snapshots exactly one writer (ledger.py), leaving the rest unasserted
- **When** each of artifact.py, transition.py, reconcile apply, telemetry.py, retro.py, critic record, decisions.py, handoff.py and sprint_report.py runs against a fixture workspace
- **Then** a before/after snapshot asserts it touched only its named target and left every other path byte-identical
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_confinement.py -k MajorWriterConfinementTests
- **Verified:** yes (2026-07-19)

### AC2: A roster sweep forces new writers in

- **Given** a side-effecting script arrives with no confinement test
- **When** the roster sweep enumerates the writers on disk against the tests that cover them
- **Then** it fails and names the uncovered script, and an entry in the explicit allowlist is the only way past
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_confinement.py -k ConfinementRosterSweepTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
