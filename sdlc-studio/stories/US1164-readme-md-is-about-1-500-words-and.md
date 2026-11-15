# US1164: README.md is about 1,500 words and opens with three routes in: evaluate, try and upgrade

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0702
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** README.md, docs/INSTALL.md, docs/why-sdlc-studio.md, tools/tests/test_lean_public_docs_retired.py, tools/tests/test_lean_docs_v63.py, tools/tests/test_lean_docs_v61.py, .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py, tools/tests/test_lint_workflow_coverage.py, tools/tests/test_install_copilot_global.py, tools/tests/test_lean_install_latest_release.py, tools/tests/test_check_versions.py, tools/tests/test_readme_front_door.py, changelog.d/US1164.md
> **Epic:** EP0310
> **Points:** 5
> **Depends on:** US1161, US1162, BG1177
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** rEADME.md is about 1,500 words and opens with three routes in: evaluate, try and upgrade
**So that** people who never open a terminal can follow progress without someone translating for them

## Acceptance Criteria

- **AC1:** Given README.md, when its words are counted as `wc -w` counts them over the whole file, then there are at most 1,800.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_readme_is_at_most_1800_words
- **AC2:** Given README.md, when its first section after the badges is read, then it offers three routes in the order evaluate, try, upgrade, and each links pages that exist: evaluate to docs/engineering-leaders.md and docs/evidence.md, try to docs/INSTALL.md, upgrade to docs/existing-users.md.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_first_section_offers_three_routes_each_to_a_page_that_exists
- **AC3:** Given the routes section first, when the v6 lead test runs, then it reads the routes section where it read 'New in 6' and still finds the current release notes link, the loop link, the FAQ upgrade answer with `migrate --apply` and at least three routes to docs/existing-users.md, none calling v6 a drop-in.
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_readme_leads_with_v6
- **AC4:** Given text cut from the README, when the tests that pin it run, then each passes where the text now lives, and none has had an assertion removed: the 6.3 cost paragraph, the coverage sentence, the Copilot row, the release-notes list and the bolded version declaration.
  - **Verify:** pytest tools/tests/test_lean_docs_v63.py::DocsV63Tests::test_the_public_pages_name_what_63_adds

## Notes

- Serves Abena Osei's End goal 5 (also 1); delivers part of CR0702 (D0479).
- AC1 must fail on: the 5,238-word README at HEAD
- AC2 must fail on: a route missing, out of order, or linking a file that does not exist
- AC3 must fail on: the lead rule deleted rather than pointed at the routes section
- AC4 must fail on: a pinned sentence dropped with no test following it to its new page
- README pins at HEAD, each of which must pass after the cut: test_lean_public_docs_retired.py:120-149 (first section after the badges starts 'New in 6', which this story changes; links the current release notes and reference-sprint.md#the-loop; a `<summary>How do I upgrade?</summary>` answer with `migrate --apply` and v5/v6; three or more lines to docs/existing-users.md; no 'drop-in'), :150 (no hand-typed counts) and :157-183 (the release-notes list names the current release); test_lean_docs_v61.py:238-242 (the upgrade answer links the 6.1 subsection of docs/existing-users.md); test_existing_users_page.py:130-146 (three routes, no drop-in); test_lean_docs_v63.py:190-202 (one paragraph with 'US dollars' naming every metered harness, 'per point', '`sprint lane run --harness <h>`' and 'headless'); test_lint_workflow_coverage.py:184-186 (the coverage sentence word for word); test_install_copilot_global.py:180-186 (a Copilot row in a tool table, no 'repo-scoped'); test_lean_install_latest_release.py:93 (no 'default install tracks `main`'); tools/check_versions.py:91 (the first bolded version declaration within the first 4,000 characters).
- Move rather than drop: worked examples, 'How it works', 'Under the hood' and the FAQ beyond the upgrade answer go to docs/why-sdlc-studio.md or docs/INSTALL.md. A pin that follows moved text is pointed at its new page, never deleted. test_lean_docs_v63.py also reads why-sdlc-studio.md's economics section.
- check_links.py already checks README's file links (ROOT_DOCS), so a dead route also fails the links lane.
- Lane: BG1177 first (same file), then this story. Needs stories B and C landed (wave 1). D is not a route target, so it is not a dependency.
- The new test carries `# test-census-subject: README.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
