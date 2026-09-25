# US0919: Sign-off is the operator's one signature and the per-unit sign-off verbs are gone

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/persona_resolve.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_resolve.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py, changelog.d/US0919.md
> **Epic:** EP0263
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator who signs each run
**I want** the per-unit `signoff`, `signoff-brief` and sign-off panel machinery gone, with `sprint sign` as the only signature
**So that** there is one way to approve a run, and no seat assignment ritual stands between a finished batch and its signature

## Acceptance Criteria

- **AC1:** Given `critic.py signoff` or `critic.py signoff-brief`, when invoked, then each exits 2 with a message that it is retired naming `sprint.py sign`, and `critic.py --help` lists neither; `sprint.py sign` by a principal the authoring session controls is still refused, so the principal-independence check (`sprint._principal_refusals`, moved off `critic.signoff_refusal`) survives. Fails on: deleting `critic.signoff_refusal` with the verbs, which drops the independence check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_verbs_are_retired
- **AC2:** Given `persona_resolve.py panel --ceremony signoff`, when invoked, then it exits 2 naming the ceremony retired; `--ceremony refine` and `--ceremony triage` still resolve their seats. Fails on: HEAD resolving the sign-off panel, and on a deletion that removes the panel verb for every ceremony
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_ceremony_is_retired_and_the_review_panel_works
- **AC3:** Given a fixture config setting `review.signoff: panel`, when `sprint.py plan` runs, then it is not refused over seat assignment; config-defaults.yaml carries no `review.signoff` and no shipped script reads it. Fails on: HEAD's plan panel refusal (sprint.py 10092-10105)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_review_signoff_has_no_reader
- **AC4:** Given a delegated-agent row in `signoff-record.md`, when the sprint report renders, then it produces no 'Delegated sign-offs' line and the file's bytes are unchanged. Fails on: HEAD's `sprint_report.py` delegated-row read (864-890)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_signoff_ledger_is_frozen_and_unread
- **AC5:** Given `docgen.py surface` rerun in the same commit, then reference-scripts-surface.md names none of `critic.py signoff` or `critic.py signoff-brief` and `docgen.py surface --check` reports 0 drift
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_the_surface_names_no_retired_verb
- **AC6:** Given the criteria whose stamped Verify selector names a test this story deletes (the signoff, panel-signoff, panel-interlock and unanswered-panel classes in `test_critic.py`, PanelAssignmentTests, SignoffPanelAssignmentTests, SignoffProvenanceTests in both suites, and the sign-off test in `test_lane_critic.py`): BG0393 (3), BG0406 (1), BG0496 (2), US0427 (3), US0598 (4), US0599 (3), US0601 (2), US0602 (2), US0643 (7) and US0644 (5), then each is retired in the D0259 pattern (`Verify: manual - retired by US0919: <why>`, `Verified: manual (<date>) - retired, superseded by US0919`), and no `Verified: yes` selector under sdlc-studio/ names a deleted test node
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_no_signoff_verbs.py::SignoffVerbsGoneTests::test_no_stamp_names_a_deleted_test

## Notes

- Deletes about 500 lines of `critic.py` (`cmd_signoff`, `record_signoff`, `signoff_brief` and the panel helpers), `persona_resolve.signoff_panel` (184-260), the plan panel refusal and the `sprint_report.py` sign-off reads left after US0917 (2553-2571).
- The principal-independence check in AC1 is moved, not deleted. It keeps an existing refusal, so it is not a new check under the ratchet rule.
- HEAD has no `review` ceremony, so AC2 names `refine` and `triage` as the surviving ceremonies.
- Engineering call: all seven of US0643's stamps retire here (PanelSignoffCliTests and SignoffPanelAssignmentTests), not split with US0917.
- Lands after US0917, and before US0923 (the panel interlock at critic.py 2231).
- The shared prose edits to `reference-scripts-review.md` and `reference-workflow-personas.md` moved to US0924.
- - Line numbers re-measured at 013a46d0: `critic.signoff_refusal` 2071, `record_signoff` 2097 (panel interlock near 2135), `signoff_brief` 3243, `cmd_signoff` 4668, `cmd_signoff_brief` 4818, parsers 4982 and 5023; `persona_resolve.signoff_panel` 197 and `--ceremony signoff` 391; `sprint._principal_refusals` 9256 still calls `critic.signoff_refusal` at 9275; the plan panel refusal is 9821-9828; `sprint_report` delegated rows 869-883 and 2646; `review.signoff: operator` at config-defaults.yaml 82. No historical status reads sign-off any more, so no licence is needed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-25 | Engineering seat | Groomed for Sprint 4 from the readiness review: 3 -> 5 points; AC1 keeps the principal-independence refusal as its control; AC2 names `--ceremony signoff` retired, with refine and triage as controls; AC4 is the delegated-row check only (the other report reads went to US0917); stamps named (10 units, 32 criteria); Affects adds test_prose_writer_hazard.py, test_sprint_report.py and the changelog fragment, and moves reference-scripts-review.md and reference-workflow-personas.md to US0924 |
| 2026-09-25 | sdlc-studio v6 planning | Sprint 5 (engineering seat): line numbers refreshed against 013a46d0; premises stand |
