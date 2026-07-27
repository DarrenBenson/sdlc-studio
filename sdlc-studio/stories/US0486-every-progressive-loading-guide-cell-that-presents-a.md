# US0486: Every Progressive Loading Guide cell that presents a path resolves

> **Status:** Ready
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

### AC2: templated and anchor forms are classified, not reported as broken

- **Given** cells carrying a templated form, a section anchor and a script invocation
- **When** the check runs
- **Then** each is classified by its own shape and none is reported as a broken link, so a new templated form does not become a false failure
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_templated_and_anchor_forms_are_classified

### AC3: the shipped guide passes

- **Given** the real SKILL.md rather than a fixture
- **When** the check runs
- **Then** it exits zero, which is true only once every resolvable cell in the shipped router actually resolves
- **Verify:** pytest tools/tests/test_check_links.py::LoadingGuideTests::test_the_shipped_guide_resolves

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
