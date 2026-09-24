# US0919: Sign-off is the operator's one signature and the per-unit sign-off verbs are gone

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py
> **Epic:** EP0263
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator who signs each run
**I want** the per-unit `signoff`, `signoff-brief` and sign-off panel machinery gone, with `sprint sign` as the only signature
**So that** there is one way to approve a run, and no seat assignment ritual stands between a finished batch and its signature

## Acceptance Criteria

- **AC1:** Given `critic.py signoff` or `critic.py signoff-brief`, when invoked, then each exits 2 with a message that it is retired naming `sprint.py sign`, and `critic.py --help` lists neither
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_verbs_are_retired
- **AC2:** Given `persona_resolve.py panel signoff`, when invoked, then it exits 2 as retired; `persona_resolve.py panel` for a review panel still resolves the product, engineering and QA seats
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_ceremony_is_retired_and_the_review_panel_works
- **AC3:** Given a fixture config setting `review.signoff: panel`, when `sprint.py plan` runs, then it is not refused over seat assignment; config-defaults.yaml carries no `review.signoff` and no shipped script reads it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_review_signoff_has_no_reader
- **AC4:** Given `signoff-record.md` present, when the sprint report renders, then it reads no row from it and the file's bytes are unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_ledger_is_frozen_and_unread
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py signoff` or `critic.py signoff-brief` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given every criterion whose stamped Verify selector names a test this story deletes (the signoff, panel-signoff, panel-interlock and unanswered-panel classes in `test_critic.py`, PanelAssignmentTests and SignoffPanelAssignmentTests; at least those on BG0393, BG0406, US0427, US0598, US0599, US0601, US0602, US0643, US0644), then each is retired as `Verify: manual - retired by <this story>` with a matching `Verified: manual` line, and no `Verified: yes` selector under sdlc-studio/ names a deleted test node, so the stamps-staged lane has nothing to refuse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_no_stamp_names_a_deleted_test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
