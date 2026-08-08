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
- **Then** it carries `## See Also`, and its `When to Use` section names TRIGGER PHRASES rather
  than a single vague sentence. The checklist's own bad example is labelled "Too vague, no
  trigger keywords", so the fault it names is vagueness and not sentence count - the assertion
  is on the trigger phrases being present, which is the rule, rather than on the shape of a list,
  which is a proxy that would outlive the reason for it
- **Verify:** pytest tools/tests/test_check_spec_claims.py::SkillSectionTests::test_skill_md_carries_the_sections_its_own_checklist_requires

### AC2: the four missing Progressive Loading rows are present

- **Given** `reference-prd.md`, `reference-story.md`, `reference-trd.md` and `reference-tsd.md`,
  none of which the Progressive Loading Guide names
- **When** the guide is read
- **Then** each has a row. These are the four documents the doctrine calls the top-level human
  levers, and an agent following the loading guide is told about neither
- **Verify:** pytest tools/tests/test_check_spec_claims.py::SkillSectionTests::test_the_four_top_level_documents_are_in_the_loading_guide

### AC3: SKILL.md's ceiling is unchanged at 500

- **Given** SKILL.md at 271 lines against a ceiling constant of 500 - which the checker
  enforces as `n >= 500`, so the effective cap is 499 and the criterion says so rather than
  restating a number that is off by one in practice
- **When** the budget is checked after the additions
- **Then** the CEILING is still 500, asserted as a value. Asserting that the file is inside its
  budget is vacuous - 229 lines of slack remain and the criterion's own projection is 296, so
  the assertion is green before a word is written - and the mutant it names, raising the
  ceiling, would make that assertion pass MORE easily rather than fail. The ceiling is the thing
  this criterion is about, so the ceiling is the thing it pins
- **Verify:** pytest tools/tests/test_check_budgets.py::DriftTests::test_skill_md_ceiling_is_unchanged

### AC4: the nesting depth is MEASURED, on a fixture whose true depth is known

- **Given** `disclosure.py`, which has no depth, nesting or hop logic of any kind today, and a
  fixture whose loading path is exactly FOUR hops deep
- **When** the depth is reported
- **Then** it reports 4, ADVISORY - exit 0 whatever the depth. US0655 puts `disclosure.py`
  into the blocking lint chain, so a non-zero exit here would couple the two units and make a
  reported measurement into a gate nobody agreed to. The fixture's depth is deliberately not the 3 this story's prose states
  about the real tree, because the mutant a hurried implementer actually writes is returning
  that constant - and a test asserting "reports the measured depth" against a tree that really
  is 3 deep passes on a hardcoded 3. The 3-hop path is not fixable without a rewrite this change
  is not doing, so the honest disposition is a number somebody can act on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_disclosure.py::DepthReachesTheReportTests::test_the_command_prints_the_depth_and_still_exits_zero

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | remove the `## See Also` section from SKILL.md | SKILL.md carries the sections its checklist requires |
| AC1 | revert `When to Use` to a single vague sentence with no trigger phrases | SKILL.md carries the sections its checklist requires |
| AC2 | drop one of the four rows from the Progressive Loading Guide | the four missing rows are present |
| AC3 | raise SKILL.md's ceiling to fit the additions | SKILL.md's ceiling is unchanged at 500 |
| AC4 | return the constant 3 that this story's prose states about the real tree | the nesting depth is MEASURED |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-08 | sdlc-studio | Plan review round 1 REJECTed both blocking findings. AC3's mutant was the wrong DIRECTION - raising a ceiling makes an inside-the-budget assertion pass more easily - and the assertion was vacuous anyway, with SKILL.md at 271 against 500; it pins the ceiling value now. AC4 was derived backwards from an implementation that does not exist: `disclosure.py` has no nesting logic at all, and the mutant a hurried implementer writes is returning the constant this story's prose states, so the fixture's true depth is deliberately four. AC1's assertion moves from list SHAPE to trigger phrases, which is what the checklist's bad example is actually about |
| 2026-08-08 | sdlc-studio | Plan review round 2 APPROVEd, ruling both round-1 findings CLOSED. Its minors are folded in: the checker enforces `n >= 500` so the effective cap is 499, and the depth report is stated ADVISORY because US0655 puts `disclosure.py` into the blocking lint chain and a non-zero exit would couple the two |
