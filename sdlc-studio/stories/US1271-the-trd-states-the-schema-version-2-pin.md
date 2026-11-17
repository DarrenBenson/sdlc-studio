# US1271: The TRD states the schema version 2 pin and the sequential era's remote scan and fetch-first defence

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0717
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0356
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TRD states the schema version 2 pin and the sequential era's remote scan and fetch-first defence
**So that** CR0717 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The TRD states this repository's schema pin and why

- **Given** section 6 and ADR-008 of `sdlc-studio/trd.md`, and `schema_version` in `sdlc-studio/.config.yaml`
- **When** the TRD's statement of the pin is read
- **Then** it gives the pinned schema version as the number the config holds, cites `sdlc-studio/.config.yaml` as where it is set, and gives the reason this repository stays on the sequential era. Fails on: a TRD that names no pin, or one whose number differs from the config's
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSequentialEraTests::test_the_pinned_schema_version_matches_the_config

### AC2: The TRD describes the sequential era's remote scan and fetch-first defence

- **Given** the TRD and `next_id.py`
- **When** the TRD's account of sequential allocation is read against the script
- **Then** it names `next_id.py --remote` reading `origin/main` without fetching, names every scan state the script defines, says allocation falls back to local ids with a warning when the remote cannot be read, and states the fetch-first precondition. Fails on: a TRD that omits the remote scan, or names a scan state the script does not have
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSequentialEraTests::test_the_remote_scan_states_match_next_id

### AC3: The seeded version and the unstamped fallback are told apart

- **Given** the TRD, `templates/config.yaml` and `templates/config-defaults.yaml`
- **When** the TRD's statement of the default schema version is read
- **Then** it names `templates/config.yaml` as the seed for a new project and `templates/config-defaults.yaml` as the fallback for an unstamped workspace, each with the version that file holds, and nowhere calls version 3 the default without saying which. Fails on: a TRD that states one default, or a version that differs from the template's
- **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdSequentialEraTests::test_the_seed_and_the_fallback_versions_match_their_templates

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
