# BG1197: Existing token-meter tests set SDLC_STUDIO_TRANSCRIPTS but leave the harness variables, so a suite run under Cursor, Copilot or OpenCode selects another meter and fails

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** conftest.py, .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py, changelog.d/BG1197.md
> **Evidence:** US0986 builder report, 2026-11-04, outside-the-unit item 1.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T11:14:12Z

## Summary

US0986's round-2 review measured the scope (2026-11-04): with `CURSOR_AGENT=1` and `CLAUDECODE` unset, 14 modules outside US0986's Affects give 90 failed, 282 passed, and 0 failed at the run's base. This is the blocking finding BG1205 carries. 2026-11-04, US0986's build (run five). US0986 chooses the meter from `SDLC_STUDIO_HARNESS`, then from harness signals such as `CURSOR_AGENT`, `COPILOT_HOME`, OPENCODE and `OPENCODE_DB.` The token tests written before it point `SDLC_STUDIO_TRANSCRIPTS` at a fixture but never clear those variables, so they pass with nothing set or under CLAUDECODE=1, and a run inside another harness selects that harness's reader and fails.

## Steps to Reproduce

1. `CURSOR_AGENT=1 python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_run_state.py .claude/skills/sdlc-studio/scripts/tests/test_retro.py`.
2. Token tests that expect the Claude fixture reading fail.

## Proposed Fix

Clear the harness variables in one shared fixture the token tests use, named from `token_meters`' own signal list so a new harness is covered when it is added.

## Acceptance Criteria

- [ ] **AC1** With `CLAUDECODE` unset and `CURSOR_AGENT=1`, the 14 meter-reaching modules BG1205 names pass, as they do under `CLAUDECODE=1`; the scrub is built from `token_meters.selection_variables()`, so a harness added later is covered.
  - **Verify:** shell env -u CLAUDECODE CURSOR_AGENT=1 python3 -m pytest -q -n auto -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_retro.py .claude/skills/sdlc-studio/scripts/tests/test_meter_reads_true.py .claude/skills/sdlc-studio/scripts/tests/test_session_tokens_once_per_message.py .claude/skills/sdlc-studio/scripts/tests/test_velocity_priced_basis.py .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py .claude/skills/sdlc-studio/scripts/tests/test_lean_velocity_row_model.py .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_keeps_window.py .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_checklist_cost.py .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_meter_any_stamp.py .claude/skills/sdlc-studio/scripts/tests/test_lean_report_meter_zero_delegated.py .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir_harness.py .claude/skills/sdlc-studio/scripts/tests/test_lean_transcript_dir.py
  - **Verified:** yes (2026-11-04)
- [ ] **AC2** The same holds with `SDLC_STUDIO_HARNESS=cursor`, with `COPILOT_HOME` beside `CLAUDECODE=1`, and with `OPENCODE_DB` set, each checked in one test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_env_isolation.py
  - **Verified:** yes (2026-11-04)

## Impact

A contributor working in Cursor, the harness CR0611 serves, sees a red suite that has nothing to do with their change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-04 | Claude Opus 5.5 (orchestrator) | Re-scoped under D0405 to the shared scrub BG1205's blocking finding needs: 2 points, root conftest.py, executable criteria over the 14 modules |
