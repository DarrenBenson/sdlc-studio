# US0865: the report of record carries every goal clause with its own verdict and evidence, and counts operator rulings against persona rulings

> **Status:** Draft
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0258
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the report of record carries every goal clause with its own verdict and evidence, and counts operator rulings against persona rulings
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: every goal clause appears in the report with its own verdict and evidence.**
  - **Given** a sealed run whose clauses evaluated to a mix of green, failed and unknown
  - **When** the report of record is derived
  - **Then** it carries one row per clause, in the authored order, each with its verdict and the evidence its check produced
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::GoalClauseSectionTests::test_every_clause_renders_with_its_verdict_and_evidence
- [ ] **AC2: the clause rows are part of the fingerprinted figure set.**
  - **Given** the same report
  - **When** a clause verdict changes and the page is re-derived
  - **Then** the fingerprint changes - a signed page whose goal evidence sits outside the digest is not signed over its goal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::GoalClauseSectionTests::test_a_changed_clause_verdict_moves_the_fingerprint
- [ ] **AC3: the report counts operator rulings against persona rulings.**
  - **Given** a run recording both kinds
  - **When** the report is derived
  - **Then** it carries both counts separately - this is the number RFC0060 exists to move, and it cannot be managed while it is visible only by reading a decisions log afterwards
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::GoalClauseSectionTests::test_operator_and_persona_rulings_are_counted_separately
- [ ] **AC4: a run with no clauses renders the section as explicitly empty.**
  - **Given** a legacy run sealed before clauses existed
  - **When** its report is re-derived
  - **Then** the section is present and states that the run recorded no clauses - an absent section reads as "not checked", and every historical report would otherwise quietly gain a gap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::GoalClauseSectionTests::test_a_legacy_run_renders_an_explicitly_empty_section

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint_report.py`, render only the overall verdict and omit the per-clause rows | every clause renders |
| AC2 | in `sprint_report.py`, add the clause rows to `OUTSIDE_THE_DIGEST` so they do not enter the fingerprint | a clause verdict moves the fingerprint |
| AC3 | in `sprint_report.py`, report one combined ruling count rather than splitting operator from persona | the two counts are separate |
| AC4 | in `sprint_report.py`, omit the section entirely when a run recorded no clauses | a legacy run renders empty |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
