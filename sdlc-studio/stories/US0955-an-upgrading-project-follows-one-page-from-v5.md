# US0955: An upgrading project follows one page from v5 to v6

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/existing-users.md, .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py, tools/tests/test_lean_upgrade_page_docs.py, changelog.d/US0955.md
> **Epic:** EP0266
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead with a v5 project in production
**I want** docs/existing-users.md to open with how to upgrade to v6: run migrate, what it removes, what I must change
**So that** I upgrade without discovering a removed gate by being refused

## Acceptance Criteria

- **AC1:** Given docs/existing-users.md, then it opens with an 'Upgrading to v6' section that tells the reader to run `migrate` then `migrate --apply`, lists what it removes, and maps each retired verb, flag, config key and check id (the union US0924's test derives) to its replacement or migrate step; outside that section it names none of them. Fails on: HEAD's title 'SDLC Studio v5 for existing projects', lines 40-50 (`testplan withdraw` and `mutation.py register --anchor` taught as current), 68 (`review.test_plan_after` as a dormant gate) and 80 (verification-depth tiers as a quality floor); a section that lists the names with no replacement
  - **Verify:** pytest tools/tests/test_lean_upgrade_page_docs.py::UpgradePageTests::test_the_upgrade_page_maps_every_retired_surface
  - **Verified:** yes (2026-09-28)
- **AC2:** Given the page's upgrade-steps block, when `test_existing_users_page.py` parses and executes it against a fixture, then every step runs, and the test no longer pins the retired keys as dormant rows or the page title to v5. Fails on: rewriting the page while `GATE_TABLE` and `DORMANT_ROWS` (lines 39-49) still require `review.two_role_after` and `review.test_plan_after` rows, so the test goes red on a correct page
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py::PageStepsAreExecutedTests::test_the_pages_own_steps_are_parsed_and_executed
  - **Verified:** yes (2026-09-28)
- **AC3:** Given the page, then it gives the path for a project last upgraded on v4 or earlier (the path the migration rehearsal walked on the two consuming projects recording 4.1.0 and 2.4.1), naming what `migrate` does across schema 2 and what it leaves to a human, and links docs/upgrade-rehearsal-v6.md. Fails on: a page that assumes every reader is on 5.1, while both consuming projects on this machine record 4.1.0 and 2.4.1
  - **Verify:** pytest tools/tests/test_lean_upgrade_page_docs.py::UpgradePageTests::test_the_upgrade_page_covers_an_older_project
  - **Verified:** yes (2026-09-28)

## Notes

- Depends on: US0925, US0954
- Folds in QA's N11 AC2 and takes US0926 AC4 (existing-users.md leaves US0926). Measured: `test_existing_users_page.py` pins the page title 'SDLC Studio v5 for existing projects' and rows for `review.two_role_after`/`review.test_plan_after` (lines 39-49, 131); this unit rewrites those pins rather than adding a new one. Rehearse by hand on a copy of a consuming project (it holds signoff-record.md, sprint-review-record.md and 12 stories with retired fields) and record the result on the story; it is not a pinned test.
- - 2026-09-27 re-measure (product seat, dee380d9): AC1 and AC2 premises hold. The old AC3 (`rehearse-release.sh upgrade` passes) is retired in the LC-002 pattern: neither rehearsal mode reads this page, so it cannot fail on the page's content, and `upgrade` rehearses a v4-era fixture while `upgrade-v5` (US0938) rehearses 5.1. Replaced by AC3, the older-project path, which the rc.1 notes' promise of a two-project rehearsal makes real.
- Its criteria move from the shared `test_lean_public_docs_retired.py` to its own `tools/tests/test_lean_upgrade_page_docs.py`, importing US0924's list, so it no longer waits on US0954. Depends on US0924 and the migration-rehearsal unit (the record AC3 links).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U4) |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: AC1 re-measured and the union imported from US0924; own test module; AC3 (vacuous rehearsal) retired and replaced by the older-project path linked to the rehearsal record; points stay 3 |
