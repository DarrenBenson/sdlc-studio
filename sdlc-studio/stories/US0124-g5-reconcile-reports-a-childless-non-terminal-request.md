# US0124: G5 reconcile reports a childless non-terminal request as UNDECOMPOSED

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0033
> **Points:** 2

## User Story

**As an** operator keeping the backlog honest
**I want** `reconcile` to report a non-terminal request with no children as UNDECOMPOSED
**So that** the intake queue cannot silently become a graveyard of requests nobody turned into work.

## Acceptance Criteria

### AC1: a request accepted into the workflow with no children is UNDECOMPOSED

- **Given** a CR or RFC accepted into the workflow (an Approved/In-Progress CR, an In-Review RFC), non-terminal, that nothing names as its Parent
- **When** `reconcile detect` runs
- **Then** it reports an `undecomposed` drift item for that request
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::UndecomposedDriftTests
- **Verified:** yes (2026-07-15)

### AC2: intake, parked, decomposed and terminal requests are not flagged

- **Given** a still-`Proposed`/`Draft` request (pre-triage intake), a `Deferred`/`Blocked` request (parked), a request with at least one child, and a terminal (Complete/Rejected) request with none
- **When** `reconcile detect` runs
- **Then** none is reported UNDECOMPOSED - the check is specific to a live, accepted, childless request, so a healthy backlog leaves `reconcile detect` clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::UndecomposedDriftTests
- **Verified:** yes (2026-07-15)

### AC3: undecomposed is a registered, hinted drift kind

- **Given** the new drift kind
- **When** the reconcile drift-kind conformance and remediation-registry tests run
- **Then** `undecomposed` is in `DRIFT_KINDS`, emitted by a detector, and carries a remediation hint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::DriftKindVocabularyTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-15 | sdlc-studio | ACs written + delivered; AC1/AC2 tightened to the accepted-not-intake rule (a Proposed/Draft request is exempt) so `reconcile detect` stays clean on a healthy backlog |
