# US0954: The repository's front door describes v6 and teaches no retired surface

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** README.md, CONTRIBUTING.md, docs/INSTALL.md, tools/tests/test_lean_public_docs_retired.py, changelog.d/US0954.md
> **Epic:** EP0266
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer landing on the repository for the first time or after an upgrade
**I want** the README, CONTRIBUTING and install guide to describe v6 and name no retired verb, flag, key or check
**So that** the first page I read agrees with the tool I install

## Acceptance Criteria

- **AC1:** Given the retired surface US0924's test derives (imported, never restated), then none of README.md, CONTRIBUTING.md and docs/INSTALL.md names one except inside a 'Removed in v6' passage. Fails on: HEAD README 136 ('verification-depth tiers (a bug cannot reach Fixed'), 209 (the mermaid edge `two-role review + sign-off`) and 469 ('two-role review' among the site's concept guides); a second hand list of retired names in this module, which misses the next retirement
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_front_door_teaches_no_retired_surface
- **AC2:** Given README.md, then its first section after the badges is 'New in 6', it links docs/release-notes-v6.0.0.md and `reference-sprint.md#the-loop`, its FAQ upgrade answer describes the v5-to-v6 path through `migrate --apply`, and it keeps at least three routes to docs/existing-users.md (the count `test_existing_users_page.py` requires), none calling v6 a drop-in. Fails on: HEAD's 'New in 5.1' section (line 23), line 180 and FAQ 414 ('two v5 gates refuse work on day one'), and no link to the loop
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_leads_with_v6
- **AC3:** Given README.md, then it states no test or script count typed by hand. Fails on: HEAD line 450 ('4,000+ unit tests'; 7,628 test functions at 013a46d0)
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_pins_no_hand_count
- **AC4:** Given README.md, CONTRIBUTING.md and docs/INSTALL.md, then every verified-install example pins the release tag `check_versions.py` reports, the README's release-notes list names 6.0.0 as current and no older release as 'the current stable release', and CONTRIBUTING's paperwork rule names a `changelog.d/<UNIT-ID>.md` fragment. Fails on: HEAD README 89 (`--version v5.1.0`, so a newcomer copying the verified install gets v5) and 479 (v5.1.0 'the current stable release'), INSTALL 162 (`v5.0.1`), CONTRIBUTING 91-92 (a `CHANGELOG.md [Unreleased]` entry)
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_contributing_and_install_are_current

## Notes

- Depends on: US0925, US0924, US0953
- Folds in QA's N11 (no user-facing page outside the skill teaches a retired surface): this unit creates `tools/tests/test_lean_public_docs_retired.py` and its registry-derived helper; U4 and D1 add their documents' tests to the same module. The README version line is release engineering's (`check_versions.py`). Takes the README half of US0926 AC3 (the mermaid edge). Ratchet (LC-008): the retired list is derived from the code's registries plus US0924's one phrase list, never a second hand list.
- - 2026-09-27 re-measure (product seat, dee380d9): premises hold; README still leads with 5.1. The union now comes from US0924's module (every script's `RETIRED_VERBS`, not only sprint's and verify_ac's: critic and mutation have registries too). AC2 takes the README link to the loop from US0956 AC2, since this unit owns README.md whole. AC4 adds the README install pin and release list: the test ties the pin to `check_versions.py`, so the cut's version bump must move the pin too (the class of the v5.0.1 pin incident).
- Depends on US0924 (the retired list) and US0953 (the notes file the README links must exist for check_links).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U3) |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: the union is imported from US0924; AC2 gains the loop link (from US0956) and the FAQ; AC4 gains the README pin and release list; Fails-on lines re-measured; points stay 3 |
