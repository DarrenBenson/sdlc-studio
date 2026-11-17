# US1208: Repo map outline and where print each symbol's line range from the index and refuse a stale index

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0678
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/reference-repo-map.md, .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py
> **Epic:** EP0330
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Repo map outline and where print each symbol's line range from the index and refuse a stale index
**So that** CR0678 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Outline prints each symbol's start-end range

- **Given** a fixture repository with a built index and a Python file holding a class with two methods and a module-level function
- **When** `repo_map.py outline <file>` is run
- **Then** it prints one line per symbol, in file order, with the symbol's name, its kind and its start-end line range, each range ending at the symbol's own last line, and it reads them from the index without parsing the file again. Fails on: a start line with no end, or a range that runs to the line before the next symbol and so takes in blank lines and comments that are not the symbol's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py::OutlineWhereTests::test_outline_prints_each_symbols_name_kind_and_line_range

### AC2: Where prints the file and range of every definition

- **Given** a built index in which one symbol name is defined in two files and another name is defined nowhere
- **When** `repo_map.py where <symbol>` is run for each
- **Then** the first prints both files, each with its start-end range, and the second exits non-zero naming the symbol and prints no range. Fails on: only the first definition printed, or an unknown symbol answered with exit 0 and no output
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py::OutlineWhereTests::test_where_prints_every_definition_and_refuses_an_unknown_symbol

### AC3: A stale index never prints wrong lines

- **Given** an index built before ten lines were inserted above a function in an indexed file, and a second indexed file left unchanged
- **When** `repo_map.py outline` and `repo_map.py where` are run for the edited file's function and for the unchanged file
- **Then** the edited file's function is printed at its new range after a rebuild, or the command exits non-zero naming the stale file and `repo_map.py build`; the unchanged file is served from the index as built; a missing index is refused the same way. Fails on: the function printed at the range the stale index holds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py::OutlineWhereTests::test_a_stale_index_is_rebuilt_or_refused_never_printed

### AC4: The reference page and the help name both verbs

- **Given** reference-repo-map.md and `repo_map.py --help`
- **When** each is read
- **Then** both name `outline` and `where`, what each prints, and what a stale index does. Fails on: a page that still lists only build, query and stats
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py::OutlineWhereTests::test_the_reference_page_and_help_name_outline_and_where

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
