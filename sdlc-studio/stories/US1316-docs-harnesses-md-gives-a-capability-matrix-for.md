# US1316: docs/harnesses.md gives a capability matrix for the six harnesses, every cell verified against the installers and scripts or marked untested, with a fallback for every harness-specific feature

> **Status:** Ready
> **Risk-class:** standard
> **Delivers:** CR0742
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/harnesses.md, tools/tests/test_harness_matrix_doc.py, changelog.d/US1316.md
> **Epic:** EP0377
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** docs/harnesses.md gives a capability matrix for the six harnesses, every cell verified against the installers and scripts or marked untested, with a fallback for every harness-specific feature
**So that** CR0742 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The matrix covers six harnesses and seven capabilities

- **Given** `docs/harnesses.md`
- **When** its capability matrix is parsed
- **Then** it has one row per harness, alphabetical (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and opencode), and the columns install path, invocation, skill discovery, parallel or sub-agents, token and cost reporting, hooks and gates, and live reload. Fails on: a harness missing, rows out of order, or a column missing
- **Verify:** pytest tools/tests/test_harness_matrix_doc.py::HarnessMatrixDocTests::test_the_matrix_has_six_harnesses_and_seven_capabilities

### AC2: Every install path matches the installer

- **Given** the matrix's install-path cells and `install.sh`'s target table
- **When** each harness's global and project paths are compared with the installer's
- **Then** they agree for every harness the installer serves, Cursor through the `agents` target. Fails on: a path the installer does not use, shown by a copy of the page with one path altered
- **Verify:** pytest tools/tests/test_harness_matrix_doc.py::HarnessMatrixDocTests::test_install_paths_match_the_installer

### AC3: Every cell is verified or marked untested

- **Given** every capability cell in the matrix
- **When** it is read
- **Then** it either says untested or names the file in this repository that shows it, and every file it names exists. Fails on: a claim with no source, or a source path that does not exist
- **Verify:** pytest tools/tests/test_harness_matrix_doc.py::HarnessMatrixDocTests::test_every_cell_is_verified_or_marked_untested

### AC4: Every harness-specific feature states its fallback

- **Given** the page's harness-specific features, at least `epic implement --agentic`, the git hooks, live reload and the token meter
- **When** each is read
- **Then** it states what a harness without it does instead (for `--agentic`: the same stories run one at a time in dependency order, through the same gates). Fails on: a harness-specific feature with no fallback stated
- **Verify:** pytest tools/tests/test_harness_matrix_doc.py::HarnessMatrixDocTests::test_every_harness_specific_feature_names_a_fallback

## Notes

- Verify each cell against `install.sh`, `install.ps1`, the skill's scripts (for example the token meter's per-harness readers) and the help pages; what nothing in the tree shows is untested, not supported.
- LC-019: a lane that adds a test file runs `tools/tests/test_test_census.py`, `tools/tests/test_boundary_marker.py` and `tools/tests/test_lean_docs_v61.py` before handing back (BG1587).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
