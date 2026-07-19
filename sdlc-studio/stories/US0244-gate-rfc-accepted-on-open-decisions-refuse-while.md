# US0244: gate RFC -> Accepted on open decisions (refuse while any Open decision stands; recorded-override escape)

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/validate.py
> **Epic:** EP0079
> **Points:** 3

## User Story

**As a** design owner accepting an RFC
**I want** the accept step to refuse mechanically while a decision is still Open
**So that** an RFC cannot be accepted, decomposed and delivered on an undecided design

## Acceptance Criteria

### AC1: Refuse RFC to Accepted while any decision row is Open

- **Given** an RFC in Draft or In Review whose Open Decisions table carries at least one row with status Open
- **When** a transition to Accepted is attempted
- **Then** transition.py refuses, naming each still-Open decision by its number, and the RFC keeps its current status
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_transition.py -k RfcOpenDecisionGateTests

### AC2: Escape only through a recorded override

- **Given** an RFC with an Open decision row and a recorded `> **Decision-Override:**` field giving the reason
- **When** the same transition to Accepted is attempted
- **Then** it succeeds, reporting the override reason, and a bare `--force` without the recorded field does not bypass the gate
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_transition.py -k RfcDecisionOverrideTests

### AC3: Report an already-Accepted RFC that still carries an Open decision

- **Given** an RFC already in Accepted whose decision table still has an Open row
- **When** validate.py runs over it
- **Then** it reports the RFC as a failure, naming the Open rows, so the gate covers files that predate it as well as new transitions
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k AcceptedRfcOpenDecisionTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
