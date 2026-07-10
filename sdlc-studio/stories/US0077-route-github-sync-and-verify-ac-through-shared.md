# US0077: Route github_sync and verify_ac through shared discovery and unify root flag

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0181

## User Story

**As a** skill maintainer
**I want** github_sync and verify_ac to use the shared discovery layer and one root-flag grammar
**So that** lowercase-named artefacts are not silently missed and the script contract is consistent

## Acceptance Criteria

### AC1: Shared discovery, no missed artefacts

- **Given** a repo using the tolerated lowercase filename convention
- **When** sync and verify run
- **Then** both find every artefact (via sdlc_md.artifact_files), with no bespoke case-sensitive glob
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py -k lowercase
- **Verified:** yes (2026-07-10)

### AC2: Unified --root grammar

- **Given** the script CLIs
- **When** `--root` is passed
- **Then** github_sync accepts it (resolving STATE_PATH against it) and verify_ac aliases it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k "root_is_alias_of_repo_root or dir_and_report_resolve_against_root"
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
