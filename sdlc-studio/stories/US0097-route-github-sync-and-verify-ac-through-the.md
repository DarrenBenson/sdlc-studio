# US0097: Route github_sync and verify_ac through the shared discovery layer

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0021
> **Persona:** Engineering seat
> **Affects:** scripts/github_sync.py, scripts/verify_ac.py, scripts/tests/test_github_sync.py

## User Story

**As a** maintainer of the skill's tooling
**I want** `github_sync` and `verify_ac` to discover artefacts through the shared `sdlc_md` layer and share one root-flag grammar
**So that** a case-sensitive glob or a cwd-relative path in one forked discovery layer stops silently missing artefacts

Delivers CR0181. No new behaviour beyond correct discovery + a consistent `--root`.

## Acceptance Criteria

### AC1: Lowercase-named artefacts sync and verify fully

- **Given** a fixture repo whose artefact filenames are lowercase
- **When** `github_sync` and `verify_ac` run over it
- **Then** every artefact is discovered (no case-sensitive-glob miss) in both tools
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py::SharedDiscoveryTests

### AC2: github_sync honours --root and STATE_PATH resolves against it

- **Given** `github_sync --root <dir>` invoked from outside the repo root
- **When** it runs
- **Then** it discovers artefacts under `<dir>` and `STATE_PATH` resolves against `<dir>`, not the cwd
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py::RootFlagTests

### AC3: verify_ac accepts --root as an alias of --repo-root

- **Given** `verify_ac.py run --root <dir>`
- **When** invoked
- **Then** it is accepted (alias of `--repo-root`), so the flag grammar matches every sibling script
- **Verify:** grep -E "\"--root\"|'--root'" .claude/skills/sdlc-studio/scripts/verify_ac.py

### AC4: No duplicate type table; discovery flows through the shared layer

- **Given** `github_sync.py`
- **When** the code is inspected
- **Then** it discovers via `sdlc_md.artifact_files` / `ARTIFACT_TYPES` with no private `TYPE_DIRS` duplicate of the shared type map
- **Verify:** grep -E "artifact_files|ARTIFACT_TYPES" .claude/skills/sdlc-studio/scripts/github_sync.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0181 |
