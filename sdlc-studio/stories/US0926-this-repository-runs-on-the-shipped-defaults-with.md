# US0926: This repository runs on the shipped defaults with no stand-down keys

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/.config.yaml, sdlc-studio/definition-of-done.md, AGENTS.md, docs/existing-users.md, .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py
> **Epic:** EP0263
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator of this repository
**I want** `migrate --apply` run on this repository to remove D0255's stand-down keys and retired check tags, with AGENTS.md and the upgrade page naming no deleted gate
**So that** the repo dogfoods exactly what a consuming project gets, with no config propping up gates that no longer exist

## Acceptance Criteria

- **AC1:** Given this repository after `migrate.py --apply`, then `sdlc-studio/.config.yaml` holds none of the retired keys, including every D0255 stand-down key, and `sdlc-studio/definition-of-done.md` carries no retired check tag
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_the_repo_config_holds_no_retired_key
- **AC2:** Given a mirror of this repository on the stripped config, when a story with green criteria and an independent delivery APPROVE is moved to Done, then it succeeds with no plan review, test plan, sign-off, depth or mutation evidence asked for, and the same story with no verdict is still refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_the_lean_path_holds_on_the_real_config
- **AC3:** Given AGENTS.md, then its refusal table names no retired gate (brief provenance on `critic record`, `critic signoff`, `Verification depth` on `transition -> Fixed`, the two-role rule on `transition -> Done`) and its lane roster names no deleted lane (`derived-depth`, `evidence-drift`)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_agents_md_names_no_retired_gate
- **AC4:** Given docs/existing-users.md, then its upgrade table names no retired key and points an upgrading project at `migrate`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_repo_defaults.py::RepoDefaultsTests::test_the_existing_users_page_names_no_retired_key

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
