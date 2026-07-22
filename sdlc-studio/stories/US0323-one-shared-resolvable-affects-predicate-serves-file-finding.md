# US0323: One shared resolvable-Affects predicate serves file_finding, artifact new and refine apply, so a future writer cannot be added without it

> **Status:** Draft
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0400
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py,.claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py
> **Epic:** EP0110
> **Points:** 3

## User Story

**As an** agent minting artefacts through whichever creation command the task calls for
**I want** one predicate deciding whether a declared `Affects` resolves, reached by every
writer
**So that** the same path cannot be refused by one command and accepted by another, and a
fourth writer added later cannot quietly skip the check

## Context

The check is not missing, it is on one door of three. `file_finding.check_groomed` borrows
`sprint.breakdown` - the planner's own predicate, not a copy - and so already refuses a bug or
CR whose declared paths all resolve to nothing. `artifact.new` calls the same helper but only
for `GROOMED_TYPES = ("bug", "cr")`, so a story minted with a wrong path is written without a
word; `refine` passes its `title|points|affects` third field straight through to
`artifact.new`, inheriting the same silence for every story in a decomposition.

This story is the predicate and its reach. US0324 is what the writers do with the verdict.

## Acceptance Criteria

### AC1: the three writers return the same verdict on the same declared value

- **Given** a table of `Affects` values covering the four shapes that matter - every path
  resolves, some resolve, none resolves, and the value is prose the parser cannot read as a
  path at all
- **When** each of `file_finding.file`, `artifact.new` and `refine.apply` is given each value
  in turn against the same scratch project
- **Then** all three accept exactly the same values and refuse exactly the same values, so no
  declared path exists that one command mints and another rejects
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::SharedPredicateTests::test_all_three_writers_agree_on_every_affects_shape

### AC2: every writer reaches the predicate, so a writer that bypasses it is caught

- **Given** the shared predicate replaced at its single seam by one that refuses everything
- **When** each creation entry point runs in turn - `file_finding.file`, `artifact.new`,
  `artifact.batch` and `refine.apply`
- **Then** every one of them refuses, so an entry point that resolves paths by its own means, or
  does not check at all, fails this criterion rather than passing on the agreement of AC1
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::SharedPredicateTests::test_every_writer_routes_through_the_one_predicate

### AC3: the predicate and the grooming gate cannot disagree about 'resolvable'

- **Given** the same table of values judged by the predicate and by `sprint.breakdown`, the gate
  that will later refuse to plan the unit
- **When** the two verdicts are compared, including the partly-resolvable case the gate
  deliberately allows
- **Then** they match on every row, so a unit accepted at mint is never refused at plan time for
  the field it was just checked on
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_affects_resolvable.py::SharedPredicateTests::test_the_predicate_and_the_grooming_gate_never_disagree

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: 3 acceptance criteria authored; `Affects` widened to the three writers and the predicate's home, which the placeholder value under-declared |
