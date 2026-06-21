# US0036: telemetry recorder and local jsonl schema

> **Status:** Done
> **Created:** 2026-06-21
> **Epic:** EP0008

## User Story

**As a** team running autosprint
**I want** per-unit run outcomes captured locally
**So that** estimation and calibration can become continuous, unblocking RFC0009 WS5 (RFC0014 WS1).

## Acceptance Criteria

### AC1: record appends whitelisted, non-None fields; no upload

- **Given** a run outcome
- **When** `telemetry record` runs
- **Then** it appends a JSONL line of only the recognised non-None fields (unknown keys dropped), to the gitignored `sdlc-studio/.local/telemetry.jsonl`, with no network call
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_record_omits_none_fields
- **Verified:** yes (2026-06-21)

### AC2: advisory - never raises, append-only, tolerant read

- **Given** an unwritable root or a corrupt line
- **When** record/read_all run
- **Then** a write failure is swallowed (returns the record), records append (never overwrite), and read_all skips malformed lines
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_record_never_raises_on_unwritable
- **Verified:** yes (2026-06-21)

### AC3: gitignored state dir + no leak

- **Given** a record with an unknown/secret field
- **When** record runs
- **Then** it writes under the gitignored `sdlc-studio/.local/`, not repo-root `.local/`, and drops the unknown field (no PII/secret leak)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_unknown_field_dropped
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/telemetry.py` (`record` + `read_all` + `show`; whitelisted FIELDS, none-omitted,
append, swallow-on-failure, skip-malformed; writes to the gitignored `sdlc-studio/.local/`).
Local-only, no network. WS3 (calibrate) + WS5 deferred.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0050) | Created via `new` (dogfood); critic REJECT->fixed (wrote repo-root .local/, not the gitignored sdlc-studio/.local/) |
