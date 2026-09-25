# US0955: An upgrading project follows one page from v5 to v6

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/existing-users.md, .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py, tools/tests/test_lean_public_docs_retired.py, changelog.d/US0955.md
> **Epic:** EP0266
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead with a v5 project in production
**I want** docs/existing-users.md to open with how to upgrade to v6: run migrate, what it removes, what I must change
**So that** I upgrade without discovering a removed gate by being refused

## Acceptance Criteria

- **AC1:** Given docs/existing-users.md, then it opens with an 'Upgrading to v6' section that tells the reader to run `migrate.py --apply`, lists what it removes, and maps each retired verb, flag, config key and check id (the same derived union U3 uses) to its replacement or migrate step; outside that section it names none of them. Fails on: HEAD's v5 title and day-one table teaching `review.two_role_after` and `review.test_plan_after`; a section that lists the names with no replacement
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_upgrade_page_maps_every_retired_surface
- **AC2:** Given the page's upgrade-steps block, when `test_existing_users_page.py` parses and executes it against a fixture, then every step runs, and the test no longer pins the retired keys as dormant rows or the page title to v5. Fails on: rewriting the page while `GATE_TABLE` and `DORMANT_ROWS` still require `review.two_role_after` and `review.test_plan_after` rows (the test goes red on a correct page)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py::PageStepsAreExecutedTests::test_the_pages_own_steps_are_parsed_and_executed
- **AC3:** Given the page, when the release rehearsal's upgrade path runs, then it passes. Fails on: a step naming a retired verb
  - **Verify:** shell bash tools/rehearse-release.sh upgrade

## Notes

- Depends on: US0925, US0954
- Folds in QA's N11 AC2 and takes US0926 AC4 (existing-users.md leaves US0926). Measured: `test_existing_users_page.py` pins the page title 'SDLC Studio v5 for existing projects' and rows for `review.two_role_after`/`review.test_plan_after` (lines 39-49, 131); this unit rewrites those pins rather than adding a new one. Rehearse by hand on a copy of a consuming project (it holds signoff-record.md, sprint-review-record.md and 12 stories with retired fields) and record the result on the story; it is not a pinned test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U4) |
