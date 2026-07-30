# US0486: Every Progressive Loading Guide cell that presents a path resolves

> **Status:** Review
> **Delivers:** CR0449
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, tools/check_links.py, tools/tests/test_check_links.py
> **Epic:** EP0175
> **Points:** 3

## User Story

**As a** agent following the always-loaded router to the file it names
**I want** every cell that presents a path to resolve, with templated and anchor forms classified rather than failed
**So that** the entry point every session loads cannot point at a file that is not there

## Acceptance Criteria

### AC1: a cell naming a path that does not exist is reported

- **Given** a guide cell naming a file absent from the tree
- **When** the check runs
- **Then** it reports that cell and the missing path
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_a_cell_naming_a_missing_path_is_reported
- **Verified:** yes (2026-07-30)

### AC2: anchored cells keep their existing file-and-anchor checking

- **Given** the 30 anchored cells the current link pass already resolves for both file and anchor
- **When** the new check runs
- **Then** they remain checked as file-and-anchor references; only templated forms and script invocations are classified out, so the guide's strongest existing coverage is not exempted away
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_anchored_cells_remain_fully_checked
- **Verified:** yes (2026-07-30)

### AC3: the cells the current pass cannot see are covered

- **Given** the bare unanchored cells and the non-markdown cells naming scripts and configuration, which the current link patterns are blind to because they match only .md
- **When** the check runs
- **Then** each is resolved as a path, which is the coverage this story exists to add
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_bare_and_non_markdown_cells_are_covered
- **Verified:** yes (2026-07-30)

### AC4: the guard is shown to redden on the real router

- **Given** the shipped SKILL.md, which resolves cleanly today
- **When** one cell is mutated to name a file that does not exist
- **Then** the check fails on it, proving this is a regression guard that can go red rather than an assertion that is true the moment it is written
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_the_guard_reddens_on_a_mutated_cell
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-27 | Claude Fable 5 | ACs repaired against the independent adversarial review |
