# BG1064: 15 of 69 shipped scripts are tracked without the executable bit the TRD's script contract requires, a regression of CR0064's fix

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/scripts/backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/triage.py, .claude/skills/sdlc-studio/scripts/tests/test_scripts_executable.py, changelog.d/BG1064.md, .claude/skills/sdlc-studio/scripts/tests/test_audit_cost.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RV0028 finding TRD-16; trd.md:232; `git ls-files -s` on 2026-10-18.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:44Z

## Summary

The TRD's script CLI contract (trd.md:232) requires `#!/usr/bin/env python3` and the executable bit. All 69 scripts carry the shebang, but `git ls-files -s` tracks 15 as 100644: `audit_cost`, `backfill_audit_runs`, `backlog_triage`, changelog, `close_owed`, `command_audit`, `engagement_floor`, flow, handoff, migrate, refine, `release_cut`, retro, `sprint_report` and triage. CR0064 and CR0208 item 8 fixed earlier instances; nothing guards it, so new scripts keep landing without it.

## Steps to Reproduce

`git ls-files -s .claude/skills/sdlc-studio/scripts/*.py | awk '$1=="100644"'` -> 15 rows.

## Proposed Fix

`git update-index --chmod=+x` the 15 and add a test that every shipped script is tracked 100755; or drop the rule from the contract, since every caller runs `python3 script.py`.

## Acceptance Criteria

- [ ] **AC1** Every shipped script under scripts/ is tracked with mode 100755, and a test fails when one is not
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_scripts_executable.py -k every_script_is_executable

## Impact

Running a script directly fails on some installs; a stated contract nothing holds.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
