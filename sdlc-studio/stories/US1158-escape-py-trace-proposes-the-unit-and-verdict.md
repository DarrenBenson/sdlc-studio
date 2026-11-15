# US1158: escape.py trace proposes the unit and verdict that let an escaped bug through, from the release and the files the fix touches

> **Status:** Ready
> **Risk-class:** standard
> **Delivers:** CR0693
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/escape.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/reviews/root-census.md, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, sdlc-studio/reviews/command-audit.md, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_surface.py, changelog.d/US1158.md
> **Epic:** EP0309
> **Points:** 3
> **Depends on:** US1157
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** escape.py trace proposes the unit and verdict that let an escaped bug through, from the release and the files the fix touches
**So that** a defect that escapes to production is traced to where it got through, and the mistake is not repeated

## Acceptance Criteria

- **AC1:** Given an escaped bug with `Shipped-in: v1.0.0` whose Affects name `scripts/a.py`, and two units that shipped in v1.0.0 (US0001 with Affects `scripts/a.py` approved by `Lena Marsh (product)`, US0002 with Affects `docs/x.md`), when `escape.py trace --bug BG0001` runs, then it lists US0001 first with the shared file and its recorded verdict and seat, and does not list US0002.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_the_unit_sharing_the_fixed_file_is_proposed_with_its_verdict
- **AC2:** Given `escape.py trace --bug BG0001 --confirm US0001`, then the bug's `Escaped-via` is set to US0001 and the verdict row (round, reviewer seat) is stamped as `Escaped-verdict`; given a unit that shares no file with the fix, then `--confirm` refuses naming the unit, and no unit proposed is written without `--confirm`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_a_confirmed_unit_is_recorded_and_an_unrelated_one_refused
- **AC3:** Given a bug with no `Shipped-in`, or a release that tags no unit, when `escape.py trace` runs, then it exits 2 naming what is missing and proposes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_escape_trace.py::EscapeTraceTests::test_a_bug_with_no_release_or_an_empty_release_proposes_nothing

## Notes

- Serves Abena Osei's End goal 4; delivers part of CR0693 (D0479).
- AC1 must fail on: units ranked without the shared-file test, or the verdict not read from the ledger
- AC2 must fail on: the proposal written without the operator's confirm, or a confirm accepted for an unrelated unit
- AC3 must fail on: a guess made from the bug text alone when the release is unknown (LL0009)
- Start: critic.py ledger readers (`ledger_prior_verdict`, `seat_for`/`recorded_seat` from US1061), retro.py seats (US1062/US1064) for the verdict-by-seat read, lib/sdlc_md.py find_by_id and file-history helpers the brief uses, `git tag --contains`/`git log` for the release's units. Build after US1061 lands if recorded_seat is wanted; otherwise read the Reviewer cell verbatim. Serves CR0693 AC1 (second clause).
- A new script or verb needs: a `sprint_report.NON_CEREMONY_VERBS` entry (or a close-checklist row), the regenerated `reference-scripts-surface.md`, a `### escape.py` catalogue heading, a root-census classification, a `build_parser`, and, for a script that writes files, the confinement allowlist (run twelve's lands were refused for each of these).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
