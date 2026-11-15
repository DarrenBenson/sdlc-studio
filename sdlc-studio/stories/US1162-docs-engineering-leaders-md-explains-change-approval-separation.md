# US1162: docs/engineering-leaders.md explains change approval, separation of duties, the signed report and cost in dollars a point, each claim linked to the mechanism that enforces it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0702
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/engineering-leaders.md, tools/tests/test_engineering_leaders_page.py, changelog.d/US1162.md
> **Epic:** EP0310
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** docs/engineering-leaders.md explains change approval, separation of duties, the signed report and cost in dollars a point, each claim linked to the mechanism that enforces it
**So that** every specification and every change names an accountable person, not 'the agent'

## Acceptance Criteria

- **AC1:** Given docs/engineering-leaders.md, when its sections are read, then it has one each for change approval, separation of duties (author, reviewer and signer), the signed report, and cost in dollars a point, and the page is at most 1,200 words as `wc -w` counts them.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_the_four_sections_are_present_and_the_page_is_short
- **AC2:** Given each paragraph and bullet in those four sections, when its links are read, then each carries at least one link to a script, a reference page heading or a committed record in this repository, and every link resolves to an existing file and, where anchored, an existing heading.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_every_claim_links_a_mechanism_that_exists
- **AC3:** Given the cost section, when it states a dollar figure, then the same paragraph links the committed report that holds it.
  - **Verify:** pytest tools/tests/test_engineering_leaders_page.py::EngineeringLeadersPageTests::test_every_dollar_figure_cites_its_report

## Notes

- Serves Abena Osei's End goal 2 (also 1 and 3); delivers part of CR0702 (D0479).
- AC1 must fail on: a section missing, or a page over 1,200 words
- AC2 must fail on: a claim with no link, or a link to a missing file or anchor
- AC3 must fail on: a typed '$2.27' with no link to sdlc-studio/reports/
- Mechanisms to link: transition.py (Done refused until executable criteria pass), critic.py brief and record with reference-review.md (one reviewer who did not write the unit), `sprint sign` in sprint.py and reference-sprint.md (refuses a principal who authored or reviewed a unit), reference-evidence-schema.md (the report of record and its fingerprint), release_cut.py evidence-pack and evidence_pack.py (a release's change evidence), sprint_report.py's Dollars per point row and templates/model-prices.json. The AGENTS.md gate table lists the refusals.
- Claim only what the shipped defaults enforce (BG1177 is the cautionary case: `review.author_self_check` ships as report, not block). Name configurable gates as configurable.
- Story B lands in another lane of the same wave, so this page does not link docs/evidence.md; the README story adds that route. Link reports under sdlc-studio/reports/ directly.
- Written for Abena: plain English, no command needed to follow it (End goal 5). The new test carries `# test-census-subject: docs/engineering-leaders.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
