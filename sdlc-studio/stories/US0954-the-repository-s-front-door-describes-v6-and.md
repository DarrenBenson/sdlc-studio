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

- **AC1:** Given the union of `sprint.RETIRED_VERBS`, `verify_ac.RETIRED_VERBS`, `sdlc_md.RETIRED_CHECK_IDS`, the retired config keys US0925 registers and the retired phrases US0924's test holds (two-role review, per-unit sign-off, verification-depth tiers, mutation gate, `--apply-signoff`), then none of README.md, CONTRIBUTING.md and docs/INSTALL.md names one except inside a 'Removed in v6' passage. Fails on: HEAD (README 135-136, 209, 213, 252, 452); a second hand list of retired names, which misses the next retirement; fixing the prose while leaving the mermaid edge `two-role review + sign-off`
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_front_door_teaches_no_retired_surface
- **AC2:** Given README.md, then its first section after the badges is 'New in 6', it links docs/release-notes-v6.0.0.md, and it keeps at least three routes to docs/existing-users.md (the count `test_existing_users_page.py` requires) with no route calling v6 a drop-in. Fails on: HEAD's 'New in 5.1' section
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_leads_with_v6
- **AC3:** Given README.md, then it states no test or script count typed by hand. Fails on: HEAD's '4,000+ unit tests' (7,628 test functions at 013a46d0)
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_pins_no_hand_count
- **AC4:** Given CONTRIBUTING.md and docs/INSTALL.md, then CONTRIBUTING's paperwork rule names a `changelog.d/<UNIT-ID>.md` fragment, and INSTALL's checksum example pins the release tag `check_versions.py` reports. Fails on: HEAD's CONTRIBUTING lines 91-92 (a `CHANGELOG.md [Unreleased]` entry) and INSTALL line 162 (`v5.0.1`)
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_contributing_and_install_are_current

## Notes

- Depends on: US0925, US0924, US0953
- Folds in QA's N11 (no user-facing page outside the skill teaches a retired surface): this unit creates `tools/tests/test_lean_public_docs_retired.py` and its registry-derived helper; U4 and D1 add their documents' tests to the same module. The README version line is release engineering's (`check_versions.py`). Takes the README half of US0926 AC3 (the mermaid edge). Ratchet (LC-008): the retired list is derived from the code's registries plus US0924's one phrase list, never a second hand list.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U3) |
