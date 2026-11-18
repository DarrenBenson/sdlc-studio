# US1305: The repo map answers which files import a given file and which symbols closely match a given symbol, by a stated rule

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0735
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/help/repo-map.md, .claude/skills/sdlc-studio/scripts/tests/test_repo_map_dependants.py, changelog.d/US1305.md
> **Epic:** EP0372
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The repo map answers which files import a given file and which symbols closely match a given symbol, by a stated rule
**So that** CR0735 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The map names the files that import a file

- **Given** a fixture with `pkg/risk_class.py`, a module importing it absolutely, one importing it relatively, a TypeScript file importing a sibling relatively, and a module importing `pkg.risk`
- **When** the map is built and asked for the dependants of `pkg/risk_class.py` and of the TypeScript sibling
- **Then** the absolute and relative Python importers are listed, the TypeScript importer is listed for its sibling, and the `pkg.risk` importer is not. Fails on: a name-prefix match (`pkg.risk` taken for `pkg.risk_class`), or a relative import missed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map_dependants.py::DependantsTests::test_importers_are_resolved_to_files_and_prefixes_do_not_match

### AC2: The map names near-duplicate modules by a stated rule

- **Given** two modules whose top-level symbol names overlap by at least half once case and underscores are folded, and a third that shares one name
- **When** the map is asked for files similar to the first
- **Then** the second is listed with its overlap and the third is not; `help/repo-map.md` states the rule and the threshold. Fails on: a file listed against itself, or a single shared name reported as a duplicate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map_dependants.py::SimilarTests::test_near_duplicates_are_found_by_folded_symbol_overlap

### AC3: A missing or stale map is said, never read as no result

- **Given** no index, then an index older than a file it covers
- **When** either query is run
- **Then** it exits non-zero naming `repo_map.py build`, or says which files changed since the build. Fails on: an empty answer printed as if nothing depended on the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map_dependants.py::StaleMapTests::test_a_missing_or_stale_index_is_reported_not_read_as_empty

## Notes

- The index already holds each file's imports (module strings) and symbols (name, kind, line). Resolution of a module string to a file is the new part; languages other than Python and relative JS/TS imports are listed as unresolved, not guessed.
- US1306 and US1307 build on these queries.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
