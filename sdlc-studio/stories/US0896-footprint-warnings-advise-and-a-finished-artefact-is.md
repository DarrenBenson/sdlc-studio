# US0896: Footprint warnings advise, and a finished artefact is never re-judged

> **Status:** Done
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/validate.py, sdlc-studio/.validate-warning-baseline.json, package.json, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_ratchet_story_agreement.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0262
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change
**I want** Affects and Verify warnings to be reported as advice on open work, with the warning ratchet and its 406-entry baseline deleted
**So that** a commit is never refused because a finished story names a file that was deleted on purpose, which is every entry Sprint 2 added to the baseline

## Acceptance Criteria

- **AC1:** Given a staged story whose Affects names a missing file, when the commit and `npm run lint` run, then neither refuses on it: the warning-ratchet lane, the `validate.py warning-ratchet` verb, its package.json script and sdlc-studio/.validate-warning-baseline.json are gone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py::AdvisoryWarningTests::test_no_commit_or_lint_run_is_refused_on_a_footprint_warning
  - **Verified:** yes (2026-09-24)
- **AC2:** Given a Draft story naming a missing file or an unrunnable Verify, when `validate.py check` runs, then it still prints the warning and exits 0; given a Done story, Fixed bug or Superseded unit whose Affects names a file deleted since, it prints nothing for that unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py::AdvisoryWarningTests::test_warnings_advise_on_open_work_and_skip_terminal_artefacts
  - **Verified:** yes (2026-09-24)
- **AC3:** Given the test nodes this story deletes (WarningRatchetTests, RatchetStatesTests and WarningRatchetExitCodeTests in `test_validate`, WarningRatchetLaneTests in `test_message_first_gate)`, then every stamped criterion naming one (US0480, BG0523, BG0524) is retired in the D0259 pattern (`Verify: manual - retired by <this story>: <why>`, `Verified: manual (<date>) - retired, superseded by <this story>`), so `verify_ac.py stamps --staged` passes on the deleting commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_advisory_warnings.py::RetiredCriteriaTests::test_the_warning_ratchet_criteria_are_retired
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
