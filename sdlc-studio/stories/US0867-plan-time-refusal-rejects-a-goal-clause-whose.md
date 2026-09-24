# US0867: plan-time refusal rejects a goal clause whose check reaches outside the declared domain, naming the clause and the path that left it

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0259
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** plan-time refusal rejects a goal clause whose check reaches outside the declared domain, naming the clause and the path that left it
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: a clause whose check reaches outside the domain is REFUSED at plan time.**
  - **Given** a goal clause whose check names a path no unit in the batch declares
  - **When** `sprint plan --write` runs
  - **Then** it refuses, naming the clause and the path that left the domain - this is what gives the boundary a consumer on the day it lands rather than leaving it dormant until the cord is built
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseWithinDomainTests::test_a_clause_reaching_outside_the_domain_is_refused
- [ ] **AC2: a clause inside the domain plans.**
  - **Given** a clause whose check names a path the batch declares
  - **When** the plan is written
  - **Then** it is accepted - the discriminating half, because a check that refused every clause would pass AC1 and block every run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseWithinDomainTests::test_a_clause_inside_the_domain_plans
- [ ] **AC3: an authored addition widens what a clause may reach.**
  - **Given** a boundary carrying an authored path and a clause whose check names it
  - **When** the plan is written
  - **Then** it is accepted - otherwise the addition from US0866 AC2 would be recorded and then ignored, which is the dormant-boundary failure in a different place
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseWithinDomainTests::test_an_authored_addition_widens_what_a_clause_may_reach
- [ ] **AC4: a check naming no path at all is not refused.**
  - **Given** a persona-judged clause whose check names a seat rather than a file
  - **When** the plan is written
  - **Then** it is accepted - a path test applied to a check that has no path would refuse the entire third shape D0230 admitted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseWithinDomainTests::test_a_pathless_check_is_not_refused

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, record the boundary but never test a clause's check against it | a clause outside the domain is refused |
| AC2 | in `sprint.py`, refuse a clause unless its check path matches the domain exactly, rejecting any path under a declared directory | a clause inside the domain plans |
| AC3 | in `sprint.py`, test the clause against the derived set only, ignoring authored additions | an addition widens the domain |
| AC4 | in `sprint.py`, refuse any check from which no path can be extracted | a pathless check is not refused |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - [+constraint] refusal of a goal clause reaching outside the domain: no clauses under D0253 |
