# US0389: surface the drift in the status hint and the close chain

> **Status:** Draft
> **Delivers:** CR0389
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0144
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py

## User Story

**As an** agent or operator working in this repository
**I want** installed-copy drift reported where I already look - the status hint and the close pre-flight
**So that** a stale mirror is seen at the moment it matters, instead of surviving a whole session until the operator thinks to ask

## Acceptance Criteria

### AC1: The hint carries a one-line drift advisory naming the count

- **Given** a repository that carries the forward-port drift check and an installed copy that differs from it
- **When** `status.py hint` or `status.py pillars` runs
- **Then** one advisory line names the number of differing files and the command that mirrors them, alongside the other advisories rather than in place of them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::InstalledCopyDriftAdvisoryTests::test_the_hint_names_the_differing_file_count

### AC2: A project without the check is silent, and the advisory never breaks the hint

- **Given** a consuming project with no drift check, no installed copy, a pinned copy, or a check that errors or times out
- **When** the hint runs
- **Then** no advisory is printed, no exception escapes, and the rest of the hint is unchanged - the drift surface holds to the same rule as every other advisory here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::InstalledCopyDriftAdvisoryTests::test_a_project_without_the_check_is_silent_and_never_raises

### AC3: The close pre-flight names the drift as its own blocker

- **Given** a run whose close is otherwise ready, in a repository whose installed copy has drifted
- **When** `close_preflight` runs
- **Then** the drift is one named blocker in the returned list, carrying the mirror command as its remedy, so the close reports it in the same single pass as every other unmet prerequisite
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClosePreflightDriftTests::test_installed_copy_drift_is_a_named_blocker_with_the_mirror_remedy

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc | Built: drift advisory on hint/pillars + a named close-preflight blocker, guarded by the check's presence |
