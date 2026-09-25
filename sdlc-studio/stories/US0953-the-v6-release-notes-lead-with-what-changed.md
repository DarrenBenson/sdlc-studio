# US0953: The v6 release notes lead with what changed for the person using it

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/release-notes-v6.0.0.md, tools/tests/test_lean_release_notes_v6.py, changelog.d/US0953.md
> **Epic:** EP0266
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer deciding whether to upgrade
**I want** release notes that lead with the headline and themes and source every figure
**So that** I can judge v6 from what it does for me, not from a list of unit ids

## Acceptance Criteria

- **AC1:** Given docs/release-notes-v6.0.0.md, then it opens with the one-sentence headline, lists the themes (one plan, one review, one signature; the one-page report; the ceremony that caught nothing is gone; faster feedback; it learns from its own runs), links the Breaking list and docs/existing-users.md, and names no unit id outside its disclosure line and sources footer. Fails on: notes composed from the fragments, which are id-laden
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_the_notes_lead_with_themes_not_ids
- **AC2:** Given every number in the notes, then its sentence or table row names its source (an RPT id, `gate_timing.py`, the back-to-basics review) and no sentence claims the code got smaller. Fails on: a 'two-thirds smaller' claim (production Python is 81,671 lines at v5.1.0 and 81,785 at 013a46d0)
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_every_figure_names_its_source
- **AC3:** Given the notes, then the repository's link and house-style checks pass on them. Fails on: a broken anchor into existing-users.md, or an em dash
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh

## Notes

- Depends on: US0952
- Figures available at 013a46d0: run span 14.5-59.6 h (v5 era, back-to-basics review) against 520.9, 325.0, 429.5 and 418.5 minutes (RPT0006-RPT0009, batch sizes differ); push gate median about 276 s over the last 10 runs (`gate_timing.py estimate --suite boundary-push`) against 678 s; token forecast 4.07x geo-mean error on the old seed against 1.14x, 0.50x, 1.03x, 0.51x; report front page 14 sections and 22 rows to 5 sections. Add Sprint 5 and rc.1 figures when measured. Depends on U1 for the Breaking list.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U2) |
