# US0382: resolve_root and under_root in sdlc_md.py, documented in reference-scripts.md and best-practices/script.md, a cwd-not-root test

> **Status:** Draft
> **Delivers:** CR0383
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0140
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/best-practices/script.md

## User Story

**As an** agent writing or maintaining a skill script that takes `--root`
**I want** one shared resolver in `sdlc_md.py` that both discovers the root and anchors a relative output path, with the rule written down
**So that** a script run from a subdirectory writes where its reader looks, instead of each script inventing its own path-joining idiom and half of them getting it wrong

## Acceptance Criteria

### AC1: a named root is honoured verbatim and a default root is discovered upward

- **Given** a project root holding an `sdlc-studio/` workspace, and a cwd two directories below it that is not itself a root
- **When** `sdlc_md.resolve_root` is called with `--root` unset (the family default `.`), and again with an explicitly named root elsewhere
- **Then** the default resolves upward to the real project root rather than the cwd, and the named root is returned verbatim without being second-guessed - and a cwd with no project above it resolves to itself rather than to `/`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RootResolverTests::test_named_root_honoured_and_default_discovered_from_a_subdirectory

### AC2: under_root anchors a relative output path and passes an absolute one through

- **Given** a resolved project root and a caller-supplied output path
- **When** `sdlc_md.under_root` is given a relative path such as `sdlc-studio/.local/report.json`, and separately an absolute path
- **Then** the relative one is anchored on the resolved root so the write lands where the gate reads it, and the absolute one is returned unchanged - the caller's explicit destination is never rewritten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RootResolverTests::test_under_root_anchors_relative_and_passes_absolute_through

### AC3: the rule is documented once and the existing verify_ac names delegate rather than duplicate

- **Given** `verify_ac.resolve_root`, `verify_ac.discover_root` and `verify_ac.under_root`, which `repo_map.py`, `lessons.py` and `loop_guard.py` already import
- **When** the shared implementation lands in `sdlc_md.py`
- **Then** the `verify_ac` names resolve to the shared implementation rather than a second copy, so those importers keep working, and `reference-scripts.md` plus `best-practices/script.md` state the resolver as the single sanctioned way a script resolves `--root` and anchors a relative output path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::RootResolverTests::test_verify_ac_names_delegate_and_the_rule_is_documented

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
