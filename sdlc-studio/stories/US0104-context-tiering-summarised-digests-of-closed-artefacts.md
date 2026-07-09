# US0104: Context tiering: summarised digests of closed artefacts

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0023
> **Persona:** Engineering seat
> **Affects:** scripts/digest.py, scripts/status.py, scripts/reconcile.py, templates/config-defaults.yaml, scripts/tests/test_digest.py

## User Story

**As an** operator of a long-lived repo whose closed-artefact corpus keeps growing
**I want** archived release batches summarised into digests that `status`/`hint` read instead of the full corpus
**So that** the token cost of the everyday status/planning commands stops growing with history

Delivers CR0179. Config-gated by a size threshold; no behaviour change below it.

## Acceptance Criteria

### AC1: Archiving a release batch produces a digest that status/hint read

- **Given** a fixture repo with 500+ closed artefacts, archived into a release batch with a digest
- **When** `status` / `hint` run
- **Then** they read the digests, not the original artefact files (instrumented read-path test proves the originals are not re-read)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_digest.py::DigestReadPathTests

### AC2: Token cost of status drops measurably

- **Given** the fixture repo
- **When** `status` runs against digests vs the full corpus
- **Then** the read cost (bytes/rows read) is measurably lower; the numbers are recorded in CR0179 on delivery
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_digest.py::DigestCostTests

### AC3: Digests are regenerable and drift-checked, byte-stable

- **Given** a generated digest
- **When** it is regenerated and `reconcile` checks it
- **Then** it is byte-stable (deterministic, like the CR0168 indexes) and reconcile flags any drift between a digest and its source batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_digest.py::DigestDriftTests

### AC4: A closed artefact still resolves by id to its full original

- **Given** a specific closed artefact whose row now lives in a digest
- **When** it is opened by id (including a CR0167 alias)
- **Then** it resolves to the full original file, unchanged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_digest.py::DigestIdResolveTests

### AC5: No behaviour change below the size threshold

- **Given** a repo below the configured size threshold
- **When** any command runs
- **Then** behaviour is unchanged (digests are not produced or read); the default threshold is documented
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_digest.py::DigestThresholdTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0179 (context tiering) |
