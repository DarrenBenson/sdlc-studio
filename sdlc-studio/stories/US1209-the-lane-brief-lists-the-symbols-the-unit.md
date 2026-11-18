# US1209: The lane brief lists the symbols the unit's criteria name in each Affects file, with line ranges

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0678
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py
> **Epic:** EP0330
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The lane brief lists the symbols the unit's criteria name in each Affects file, with line ranges
**So that** CR0678 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The brief lists the symbols the criteria name, with ranges

- **Given** a unit whose acceptance criteria name a function defined in one of its Affects files, and a built repo map index
- **When** `sprint.py lane brief --units <id>` is run
- **Then** the brief lists that function under its Affects file with its start-end line range. Fails on: the Affects file listed with no symbol, or the symbol given a start line and no end
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefSymbolTests::test_the_brief_lists_each_named_symbol_with_its_line_range

### AC2: A file whose symbols the criteria do not name gets the top ranked ones

- **Given** a unit with a large Affects file none of whose symbols its story or criteria name
- **When** `sprint.py lane brief --units <id>` is run
- **Then** the brief lists for that file the symbols `repo_map.py query` ranks highest for the unit's text, a bounded few, each with its range. Fails on: no symbol listed for the file, or every symbol of the file printed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefSymbolTests::test_a_file_with_no_named_symbol_lists_the_top_ranked_few

### AC3: A stale or absent index never puts wrong ranges in a brief

- **Given** a unit whose Affects names one file edited since the index was built and one file that does not exist yet
- **When** `sprint.py lane brief --units <id>` is run, and again with the index deleted
- **Then** the brief is issued both times; the edited file's ranges come from a rebuilt index or the brief says the ranges are not available and names `repo_map.py build`; the file that does not exist yet lists no symbol. Fails on: a range read from the stale index, or a brief refused because the index is missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefSymbolTests::test_a_stale_or_absent_index_gives_no_wrong_range

### AC4: The prompt template says the brief carries the ranges

- **Given** reference-agent-prompt-template.md
- **When** its section on the brief's file list is read
- **Then** it says the lane brief carries each target symbol's line range and that the builder reads those ranges before searching. Fails on: a page that still tells the dispatcher to fill the file list by hand from `repo_map.py query`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderRunbookTests::test_the_prompt_template_says_the_brief_carries_symbol_ranges

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
