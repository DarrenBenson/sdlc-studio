# US0452: The version guard reaches every authoritative home, discovered rather than hand-enumerated

> **Status:** Done
> **Delivers:** RFC0056
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_versions.py, tools/tests/test_check_versions.py
> **Epic:** EP0167
> **Points:** 3

## User Story

**As a** maintainer relying on the version guard to catch drift
**I want** the guard to find every file that declares the skill version, rather than checking a hand-written list of four
**So that** a document declaring a version is held to it from the day it is written, not from the day someone remembers to add it to the list

## Acceptance Criteria

### AC1: every declared version home is discovered and checked

- **Given** a repo whose version declarations include `sdlc-studio/trd.md` and `sdlc-studio/tsd.md`, which the four-entry list never reached
- **When** the guard runs
- **Then** it checks every discovered declaration against the authoritative version and names each one that disagrees
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveredHomesTests::test_every_declared_version_home_is_checked
- **Verified:** yes (2026-07-29)

### AC2: a new version home is covered without editing the guard

- **Given** a tracked file that newly declares a version disagreeing with the authoritative one
- **When** the guard runs with no change made to the guard itself
- **Then** it fails and names that file, because coverage follows the repo rather than a list somebody must maintain
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveredHomesTests::test_a_new_version_home_is_covered_without_editing_the_guard
- **Verified:** yes (2026-07-29)

### AC3: discovery that fails refuses to report a clean scan

- **Given** a run in which the discovery pass cannot list the files it is meant to scan
- **When** the guard runs
- **Then** it exits non-zero saying it could not scan, never reporting a clean pass over nothing
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveredHomesTests::test_failed_discovery_refuses_to_report_clean
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
