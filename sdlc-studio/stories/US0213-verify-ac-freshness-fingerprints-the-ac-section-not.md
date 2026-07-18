# US0213: verify_ac freshness fingerprints the AC section, not the file mtime

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Epic:** EP0072
> **Points:** 3

## User Story

**As an** engineer taking a verified story to Done
**I want** freshness judged on what the verifier actually ran against
**So that** a status change or a revision-history row does not force a pointless re-verify

## Acceptance Criteria

### AC1: A metadata-only edit leaves a green verify entry fresh

- **Given** a story whose executable ACs verified green, then edited only outside the Acceptance Criteria section (Status line, Revision History row, or the `**Verified:**` stamps the verifier itself writes)
- **When** the Done gate judges freshness
- **Then** the story is not blocked: the AC fingerprint is unchanged, so mtime moving is recognised as noise rather than staleness.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_transition.AcFingerprintFreshnessTests.test_metadata_edit_stays_fresh
- **Verified:** yes (2026-07-18)

### AC2: A changed AC or verifier still invalidates the green

- **Given** a verified story subsequently edited inside its Acceptance Criteria - an AC retitled, an AC added or removed, or a Verify line re-pointed at a different command
- **When** the Done gate judges freshness
- **Then** the story is blocked with a re-verify instruction, because the fingerprint no longer matches what passed.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_transition.AcFingerprintFreshnessTests.test_ac_edits_invalidate
- **Verified:** yes (2026-07-18)

### AC3: A report predating the fingerprint still falls back to mtime

- **Given** a verify-report entry written before `ac_fingerprint` existed, carrying `verified_at` but no fingerprint
- **When** the Done gate judges freshness on a story edited after that timestamp
- **Then** the mtime comparison still applies and still blocks - the new field's absence never silently passes a stale green.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_transition.AcFingerprintFreshnessTests.test_legacy_report_falls_back_to_mtime
- **Verified:** yes (2026-07-18)

### AC4: The fingerprint is written by the verifier

- **Given** a story verified by `verify_ac run`
- **When** the report is written
- **Then** the entry carries an `ac_fingerprint` matching the story's current AC content, so the gate has something to compare.
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_transition.AcFingerprintTests
- **Verified:** yes (2026-07-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Groomed: ACs and executable Verify lines authored; `Affects` corrected to include transition.py (the gate that consumes the freshness signal) |
