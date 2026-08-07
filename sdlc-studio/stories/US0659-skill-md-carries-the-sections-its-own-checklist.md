# US0659: SKILL.md carries the sections its own checklist requires, and every reference is two hops away

> **Status:** Ready
> **Delivers:** CR0538
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/scripts/disclosure.py, .claude/skills/sdlc-studio/best-practices/claude-skill.md, .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py, tools/tests/test_check_spec_claims.py, tools/tests/test_check_budgets.py
> **Epic:** EP0211
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** SKILL.md carries the sections its own checklist requires, and every reference is two hops away
**So that** CR0538 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: SKILL.md carries the sections its own best-practices file requires

- **Given** `best-practices/claude-skill.md`, which requires a `## See Also` section and gives a
  single prose sentence as its explicit BAD example of trigger phrasing
- **When** SKILL.md is read
- **Then** it carries `## See Also`, and its trigger phrasing is a list rather than the single
  sentence its own guidance names as wrong. A router that fails the checklist it ships is the
  cheapest possible finding and the most embarrassing to leave
- **Verify:** pytest tools/tests/test_check_spec_claims.py::SkillSectionTests::test_skill_md_carries_the_sections_its_own_checklist_requires

### AC2: the four missing Progressive Loading rows are present

- **Given** `reference-prd.md`, `reference-story.md`, `reference-trd.md` and `reference-tsd.md`,
  none of which the Progressive Loading Guide names
- **When** the guide is read
- **Then** each has a row. These are the four documents the doctrine calls the top-level human
  levers, and an agent following the loading guide is told about neither
- **Verify:** pytest tools/tests/test_check_spec_claims.py::SkillSectionTests::test_the_four_top_level_documents_are_in_the_loading_guide

### AC3: SKILL.md stays inside its budget

- **Given** the additions, landing SKILL.md at roughly 296 lines
- **When** the budget lane runs
- **Then** it passes against the 500-line ceiling unchanged. The router's size is the reason it
  is a router, and a section added past the ceiling would trade the property that makes it work
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_skill_md_is_inside_its_budget

### AC4: the 3-hop nesting is REPORTED, not silently left

- **Given** the loading path that reaches three references deep before an agent has what it
  needs
- **When** `disclosure.py` runs
- **Then** it reports the measured depth. It is not fixable without a rewrite this change is not
  doing, and the honest disposition is a number somebody can act on rather than a silence that
  reads as absence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py::NestingDepthTests::test_the_measured_nesting_depth_is_reported

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | remove the `## See Also` section from SKILL.md | SKILL.md carries the sections its checklist requires |
| AC1 | revert the trigger phrasing to the single prose sentence | SKILL.md carries the sections its checklist requires |
| AC2 | drop one of the four rows from the Progressive Loading Guide | the four missing rows are present |
| AC3 | raise SKILL.md's ceiling to fit the additions | SKILL.md stays inside its budget |
| AC4 | report the nesting depth as zero when it cannot be computed | the 3-hop nesting is REPORTED |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
