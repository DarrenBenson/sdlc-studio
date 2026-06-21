# US0030: skill version check + self-update signal

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0044)
> **Reviewer:** --
> **Created:** 2026-06-21
> **GitHub Issue:** --

## User Story

**As a** user of SDLC Studio
**I want** the skill to tell me when a newer release exists and offer to update it
**So that** I stay current without manual checking - and without nagging once I decline,
until a newer release ships (CR0044).

## Acceptance Criteria

### AC1: Compares installed vs latest release; degrades silently

- **Given** the installed skill version and a latest-release fetcher
- **When** `version_check.check` runs (update available / equal / offline / disabled)
- **Then** it returns the right status, never raises (a raising/None fetcher → `offline`), and makes no network call when disabled
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_version_check.py::CheckTests
- **Verified:** yes (2026-06-21)

### AC2: TTL cache + per-version snooze

- **Given** a cached latest version
- **When** checked within the TTL (no refetch), after a snooze (status `snoozed`), and when offline
- **Then** the cache is honoured, a dismissed version stays quiet until a newer one, and an offline result never overwrites the cached latest
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_version_check.py::CheckTests::test_offline_does_not_poison_cache
- **Verified:** yes (2026-06-21)

### AC3: Notice only when an update is available

- **Given** a check result
- **When** `notice()` renders it
- **Then** it returns the one-line update notice only for `update-available`, and None for up-to-date / offline
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_version_check.py::CheckTests::test_up_to_date
- **Verified:** yes (2026-06-21)

### AC4: Scope detection (user / project / agents)

- **Given** an install path
- **When** `scope` runs - including a repo checkout under $HOME
- **Then** it returns user / project / agents correctly (a checkout under $HOME is still `project`)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_version_check.py::ScopeTests
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/version_check.py` (check/snooze/scope, TTL cache, semver, silent network);
`status.py` `_print_update_notice` on status/hint (guarded); `skill-update` action
(`reference-skill-update.md` + `help/skill-update.md`); `version_check.enabled`/`ttl_hours`
config; agent-instructions note.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0044) | Decomposed from CR0044; critic APPROVE after self-degrading fixes |
