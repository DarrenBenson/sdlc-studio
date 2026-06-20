# US0029: validate no-ac honours the adoption cutoff

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** agent-crew (adopted via CR0031)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** maintainer of a project that adopted the AC discipline partway
**I want** `validate`'s `no-ac` error to honour `conformance.adopt_after`
**So that** legacy stories below the cutoff are not flagged for a missing AC section,
consistent with the conformance gate (CR0027) - without suppressing any other check.

## Acceptance Criteria

### AC1: Grandfather below the cutoff, judge at/after it

- **Given** `.config.yaml` `conformance.adopt_after: US0682`, a pre-cutoff US0100 and a post-cutoff US0700 (both without AC)
- **When** validate runs
- **Then** US0100 is exempt from `no-ac` and US0700 is still flagged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ValidateFileTests::test_no_ac_grandfathered_below_adopt_after
- **Verified:** yes (2026-06-20)

### AC2: Fail safe - no cutoff or malformed config judges every story

- **Given** no cutoff, or a malformed `.config.yaml`
- **When** validate runs on a story with no AC
- **Then** `no-ac` still fires (exemption never happens on uncertainty)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ValidateFileTests::test_no_ac_still_flagged_with_malformed_config
- **Verified:** yes (2026-06-20)

### AC3: Cutoff is exclusive

- **Given** `conformance.adopt_after: US0100` and a no-AC US0100
- **When** validate runs
- **Then** US0100 itself is still flagged (only ids strictly below the cutoff are exempt)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ValidateFileTests::test_no_ac_at_cutoff_still_flagged
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/validate.py`: `_ac_exempt(rec, repo_root)` ANDed onto the `no-ac` condition
inside the `type_ == "story"` block; reads `conformance.adopt_after` via
`sdlc_md.project_override`, exempts `id_number(rec) < cutoff`. Authored by agent-crew,
back-ported with fail-safe + boundary tests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0031) | Decomposed from CR0031; agent-crew contribution adopted; critic APPROVE |
