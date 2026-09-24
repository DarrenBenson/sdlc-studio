# US0898: A shipped release's notes stay as shipped, and the defect count is written at the cut

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, tools/tests/test_lean_release_notes.py, docs/release-notes-v5.1.0.md, docs/known-issues.md, .githooks/pre-push, tools/tests/test_pre_push_hook.py, sdlc-studio/stories/US0670-the-release-discloses-every-open-medium-and-low.md, sdlc-studio/bugs/BG0656-the-disclosure-page-s-prose-and-its-guard.md
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer filing and closing findings between releases
**I want** the open-defect count and the known-issues page to be generated when a release is cut and checked only at its tag
**So that** filing or closing a finding no longer turns the suite red until a published record is edited (the v5.1.0 notes were edited 33 times, the known-issues page 99)

## Acceptance Criteria

- **AC1:** Given a copy of this repository with one extra open Medium finding filed and nothing else changed, when the tools suite runs, then no test fails: no test compares a shipped release's notes or docs/known-issues.md with the live corpus (ReleaseNotesClaimTests and the live-page cases of KnownIssuesPageTests are gone; the generator's fixture tests stay)
  - **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_filing_a_finding_reddens_no_test
  - **Verified:** yes (2026-09-24)
- **AC2:** Given `known_issues.py write --release <version>` at the release cut, then it writes docs/known-issues.md and the open-defect sentence of that version's notes from the corpus at that moment, and refuses to rewrite the notes of a version that already has a tag
  - **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_the_cut_writes_the_page_and_only_the_untagged_notes
  - **Verified:** yes (2026-09-24)
- **AC3:** Given a tag push whose known-issues page disagrees with the corpus, when the pre-push hook runs at the release boundary, then it refuses naming `known_issues.py write`; a branch push does not run the check. This one tag-time check replaces the per-push suite comparisons and the hand-edited `NOTES_REL` pin it retires
  - **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_the_page_is_checked_at_the_tag_only
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
