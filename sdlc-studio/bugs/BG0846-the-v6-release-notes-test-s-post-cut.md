# BG0846: The v6 release notes test's post-cut control assumes the notes still carry the pre-cut links, so the v6.0.0 cut turns the tools suite red

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_init_version.py, tools/tests/test_lean_release_notes_v6.py, changelog.d/BG0846.md
> **Evidence:** v6.0.0 cut rehearsal on main after 840f5374, pytest -n 4 tools/tests: 2 failed
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T00:19:53Z

## Summary

`test_lean_release_notes_v6.py`::ReleaseNotesTests::`test_the_notes_lead_with_themes_not_ids` ends with a control that feeds the REAL notes to `lead_problems` against a synthetic post-cut CHANGELOG and asserts they are flagged for missing the 6.0.0-rc.1 section link. That holds only while the notes still point at #600---2026-09-26 and #unreleased. The v6.0.0 cut re-points both links (as the notes' own landing note requires), so the control finds nothing to flag and fails; `test_lean_release_notes.py`::FrozenNotesTests::`test_filing_a_finding_reddens_no_test` then fails too, because it re-runs that module inside its copy. Found preparing the v6.0.0 release commit on 2026-09-29 (tools suite: 2 failed, 850 passed).

## Steps to Reproduce

Apply the cut (rename [6.0.0] to [6.0.0-rc.1], changelog-cut --version 6.0.0, re-point the notes' two CHANGELOG anchors) and run tools/tests.

## Proposed Fix

Build the control's pre-cut input from the notes by reversing the re-point (post-cut anchors back to #600---2026-09-26 and #unreleased), so the control proves the flag in either layout; the moved-links case then re-points that pre-cut text. The assertion that the real notes pass against the real CHANGELOG stays.

## Acceptance Criteria

- [ ] **AC1** Given the notes and CHANGELOG after the v6.0.0 cut, then `test_the_notes_lead_with_themes_not_ids` passes, and its control still flags a pre-cut variant of the notes (links to #600---2026-09-26 and #unreleased) against a post-cut CHANGELOG. Fails on: the control reading the real notes, which the cut has already re-pointed
  - **Verify:** pytest tools/tests/test_lean_release_notes_v6.py::ReleaseNotesTests::test_the_notes_lead_with_themes_not_ids

- [ ] **AC2** Given the tree after the v6.0.0 cut (templates/version.yaml and SKILL.md at 6.0.0), then test_lean_init_version's two tests pass: each makes init, migrate and project upgrade read the version it simulates from the source init actually stamps from, not only from a mocked `installed_version`. Fails on: HEAD's tests, which pass only while templates/version.yaml happens to equal the mocked version (6.0.0-rc.1), so the cut turns them red
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_init_version.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-29 | sdlc-studio v6 | Widened to test_lean_init_version (AC2): the skill suite on the cut tree failed its two tests for the same reason, a pre-cut assumption |
