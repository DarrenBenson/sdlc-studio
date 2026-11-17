# US1244: This repository's always-loaded instruction files take the accepted cuts, sizes reported before and after

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0700
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** AGENTS.md, CLAUDE.md, sdlc-studio/personas/seats/engineering.md, sdlc-studio/personas/seats/product.md, sdlc-studio/personas/seats/qa.md, tools/tests/test_agents_md_budget.py, changelog.d/US1244.md
> **Epic:** EP0342
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** This repository's always-loaded instruction files take the accepted cuts, sizes reported before and after
**So that** CR0700 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The accepted cuts are made and the kept text stays

- **Given** CR0700's audit rows citing AGENTS.md, CLAUDE.md and this repository's three seat cards under `sdlc-studio/personas/seats/`
- **When** each cited file is read at HEAD
- **Then** the quoted text of every row dispositioned `changed` or `removed` is gone from its file, and the quoted text of every `kept` row is still there. Fails on: an accepted cut not made, or a kept rule cut along with it
- **Verify:** pytest tools/tests/test_agents_md_budget.py::AuditCutsTests::test_accepted_cuts_are_made_and_kept_text_stays

### AC2: AGENTS.md stays in budget with every gated rule's text

- **Given** AGENTS.md after the cuts
- **When** its budget, spine and pinned phrases are checked
- **Then** it is within `AGENTS_MD_BUDGET`, the constant is not raised, and the four start-here steps, every refusals row and every non-negotiable rule's paragraph survive. Fails on: a rule a gate enforces losing the text that tells an agent about it
- **Verify:** pytest tools/tests/test_agents_md_budget.py::AgentsMdBudgetTests::test_agents_md_fits_its_budget_and_keeps_its_spine

### AC3: Each file's size is reported before and after

- **Given** the size in characters CR0700's audit recorded for each of the five files
- **When** each file's size at HEAD is set against it
- **Then** no file is larger than the audit recorded, their total is smaller, and the test's failure message prints each file's before and after size in characters and estimated tokens. Fails on: a cut that leaves the always-loaded text no smaller, or a file grown by the rewrite
- **Verify:** pytest tools/tests/test_agents_md_budget.py::AuditCutsTests::test_no_file_is_larger_and_the_total_is_smaller

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
