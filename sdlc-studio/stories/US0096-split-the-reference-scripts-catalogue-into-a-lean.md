# US0096: Split the reference-scripts catalogue into a lean index

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0020
> **Persona:** Engineering seat
> **Affects:** reference-scripts.md, tools/check_budgets.py

## User Story

**As an** agent loading the script catalogue before a mechanical task
**I want** `reference-scripts.md` to be a lean index pointing to grouped detail pages
**So that** the file loads cheaply and stops needing a budget-ceiling bump every sprint

Delivers CR0200. Documentation reorganisation only - no script behaviour changes.

## Acceptance Criteria

### AC1: reference-scripts.md is a lean index under budget

- **Given** the split
- **When** the budgets guard runs
- **Then** `reference-scripts.md` is under the 600-line reference budget and its `643` allowlist entry is removed from `tools/check_budgets.py`; every grouped detail page is also under budget
- **Verify:** pytest tools/tests/test_check_budgets.py

### AC2: Every script stays catalogued (doc-coverage floor holds)

- **Given** the reorganised catalogue
- **When** `doc_coverage.py` runs
- **Then** it reports 0 undocumented scripts - every shipped script has an entry reachable from the index
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/doc_coverage.py --root . | grep -q PASS

### AC3: All links resolve and pointers still land

- **Given** the split and any updated cross-references
- **When** `check_links.py` runs
- **Then** all internal anchor links resolve, and pointers from SKILL.md and other references to `reference-scripts.md` (or its new pages) still land
- **Verify:** shell python3 tools/check_links.py

### AC4: No behaviour change

- **Given** this is a documentation reorganisation
- **When** the full skill test suite runs
- **Then** it passes unchanged (no script content or behaviour was touched)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests 2>&1 | tail -1 | grep -q OK

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0200 |
