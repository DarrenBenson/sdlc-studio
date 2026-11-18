# US1188: lessons revalidate with a citation check reports each Revalidated citation past the file's end or away from its symbol

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0657
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_lessons_check_citations.py
> **Epic:** EP0324
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** lessons revalidate with a citation check reports each Revalidated citation past the file's end or away from its symbol
**So that** CR0657 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A citation past the end of its file is reported

- **Given** a lessons log with a Revalidated reason citing `path:line` where the line is beyond the file's last, another citing a file that does not exist, and a third lesson whose citation is in range
- **When** `lessons.py revalidate --check-citations` runs
- **Then** it exits 1 and lists the first two, each with its lesson id, the citation and why; the third is not listed. A log with no such citation exits 0. Fails on: exit 0 over a citation that points at nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_check_citations.py::CheckCitationsTests::test_a_citation_past_the_files_end_is_reported

### AC2: A citation whose named symbol has moved away is reported with where the symbol is now

- **Given** a reason naming a symbol in backticks beside its `path:line`, in a fixture file where that symbol is defined many lines from the cited one; a control whose symbol is within the documented window; and a citation in range with no symbol beside it
- **When** the check runs
- **Then** only the first is reported, naming the symbol, the cited line and the line the symbol is on now; the two controls pass. Fails on: a drifted citation passing because its line still exists, which is the 16-line decay CR0657 records
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_check_citations.py::CheckCitationsTests::test_a_citation_away_from_its_symbol_is_reported

### AC3: The guidance asks a reason to name the symbol beside each line

- **Given** `help/lessons.md`'s re-validation section
- **When** an author writes a Revalidated reason
- **Then** the page asks for the symbol beside every `path:line` and documents `--check-citations`, its window and its exit codes, each as the command behaves. Fails on: guidance that leaves the check with no symbol to anchor on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_check_citations.py::CheckCitationsTests::test_the_help_asks_for_the_symbol_and_documents_the_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
