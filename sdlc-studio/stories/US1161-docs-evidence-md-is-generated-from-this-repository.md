# US1161: docs/evidence.md is generated from this repository's signed reports and explains a partial verdict, the wait for a signature and how to regenerate it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0702
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/evidence.md, tools/tests/test_evidence_page_committed.py, changelog.d/US1161.md
> **Epic:** EP0310
> **Points:** 2
> **Depends on:** US1160
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** docs/evidence.md is generated from this repository's signed reports and explains a partial verdict, the wait for a signature and how to regenerate it
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given this repository's committed reports, when `sprint_report.py evidence --out docs/evidence.md --check` runs, then it exits 0, and the page names the newest report it covers.
  - **Verify:** pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_the_committed_page_matches_the_reports
- **AC2:** Given docs/evidence.md, when its hand-written part is read, then it has a section on what 'Judged partial' means and where its reason comes from, one on how the wait for a signature is measured (report built to report signed), and one naming the command that regenerates the page, and every link in them resolves to an existing file and heading.
  - **Verify:** pytest tools/tests/test_evidence_page_committed.py::CommittedEvidencePageTests::test_the_page_explains_partial_verdicts_waiting_and_regeneration

## Notes

- Serves Abena Osei's End goal 1 (also 5); delivers part of CR0702 (D0479).
- AC1 must fail on: a hand-edited cell, or a page with no generated table
- AC2 must fail on: a section missing, or a link to a file or anchor that does not exist
- Run the story-A verb on the real reports; never type a figure. Ten of the 28 signed runs read 'Judged partial' at HEAD (29 signed reports; RPT0017 and RPT0018 are one run), and RPT0022 waited about 3.8 days for its signature, so the explanation matters.
- check_links.py does not scan docs/*.md file links (only CHANGELOG anchors there), so the test checks this page's links itself; reuse check_links.slug for anchors.
- Same lane as A, after it. The new test carries `# test-census-subject: docs/evidence.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
