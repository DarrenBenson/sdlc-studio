# US0953: The v6 release notes lead with what changed for the person using it

> **Status:** Done
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

- **AC1:** Given docs/release-notes-v6.0.0.md, then it opens with a one-sentence headline naming 6.0.0 as the current release, lists the themes (one plan, one review, one signature; the one-page report; the ceremony that caught nothing is gone; faster feedback; it learns from its own runs), links the CHANGELOG's 6.0.0 and 6.0.0-rc.1 sections and docs/existing-users.md, carries no release-candidate framing, and names no unit id outside its known-issues and sources passages. Fails on: the rc.1 notes copied with the version changed, which still say 'v5.1.0 remains the current stable release' and 'This is a release candidate'; notes composed from the fragments, which are id-laden
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_the_notes_lead_with_themes_not_ids
  - **Verified:** yes (2026-09-28)
- **AC2:** Given the notes, then they carry an 'Upgrading from 6.0.0-rc.1' section (reinstall with `--version v6.0.0`, what changed since the candidate, and that an installed candidate is now prompted to move) and an 'Upgrading from 5.1' section whose steps are `migrate` then `migrate --apply`, with what each leaves to the reader. Fails on: notes that address only a 5.1 reader, leaving everyone who installed the candidate with no path
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_both_upgrade_paths_are_given
  - **Verified:** yes (2026-09-28)
- **AC3:** Given every number in the notes, then its sentence or table row names its source (an RPT id, `gate_timing.py`, the back-to-basics review, the rehearsal record, the eval run) and no sentence claims the code got smaller. Fails on: the rc.1 notes' unsourced '82% of this repository's sprint units served its own machinery'; a 'two-thirds smaller' claim (production Python measured 81,671 lines at v5.1.0 and 81,785 at 013a46d0)
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_every_figure_names_its_source
  - **Verified:** yes (2026-09-28)
- **AC4:** Given the notes, then they report the soak the candidate's notes promised: the migration rehearsed on two consuming projects (linking docs/upgrade-rehearsal-v6.md), the eval re-run (its result, and any scenario not run named as such), and the website project's lean sprint on the candidate, each with the findings it filed. Fails on: dropping a promise made in public ('the migration is rehearsed on two real consuming projects, with the record linked from the 6.0.0 notes'; 'the eval scenarios are re-run against v6 behaviour')
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_the_soak_promises_are_reported
  - **Verified:** yes (2026-09-28)
- **AC5:** Given the notes, then `tools/check_links.py` and `tools/lint-style.sh` pass and the notes carry exactly one `**v6.0.0 discloses N open defects: N Medium, N Low.**` line for `known_issues.py write --release 6.0.0` to fill. Fails on: a broken anchor, an em dash, or a missing count line, which makes the cut refuse
  - **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && test "$(grep -cE '^\*\*v6\.0\.0 discloses [0-9]+ open defects' docs/release-notes-v6.0.0.md)" = 1
  - **Verified:** yes (2026-09-28)

## Notes

- Depends on: US0952
- Figures available at 013a46d0: run span 14.5-59.6 h (v5 era, back-to-basics review) against 520.9, 325.0, 429.5 and 418.5 minutes (RPT0006-RPT0009, batch sizes differ); push gate median about 276 s over the last 10 runs (`gate_timing.py estimate --suite boundary-push`) against 678 s; token forecast 4.07x geo-mean error on the old seed against 1.14x, 0.50x, 1.03x, 0.51x; report front page 14 sections and 22 rows to 5 sections. Add Sprint 5 and rc.1 figures when measured. Depends on U1 for the Breaking list.
- - 2026-09-27 re-measure (product seat, dee380d9): docs/release-notes-v6.0.0-rc.1.md exists and is the base: its 'What v6 is', 'Breaking changes' and 'Upgrading from v5.1' sections carry forward. What 6.0.0 needs beyond it: no candidate framing; an rc.1-to-6.0.0 upgrade path (BG0790); 'since the candidate' (BG0790, CR0599 with BG0788: a signature any clone can verify, BG0784, BG0785, the three [Unreleased] fixes BG0776, BG0774, BG0793, the docs rewrite); the soak evidence rc.1 promised (AC4); the known-issues limits restated (drop the signing-clone limit once CR0599 lands, drop BG0790); sourced figures; the CHANGELOG layout after the rename (Breaking inventory under 6.0.0-rc.1, pointed at from 6.0.0); the verified install pinned to v6.0.0.
- Written last in the sprint: depends on US0952, the migration-rehearsal unit and the eval unit, and reads the website sprint's close for its figures (cross-repository, a note not a Depends on).
- The notes are a one-off document, so a durable test module is a cost every push pays; engineering may prefer shell checks. Kept as pytest because four criteria parse structure.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (U2) |
| 2026-09-27 | sdlc-studio v6 planning | Product seat, Sprint 6 re-measure at dee380d9: re-based on the rc.1 notes; adds the rc.1 upgrade path (AC2), the soak the rc.1 notes promised (AC4) and the known-issues count line (AC5); points stay 3 |
