# BG1671: init.py writes no personas.standard, so a project created at the persona-standard release is switched to report mode by its first later project upgrade

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_standard_mode.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:46:41Z

## Summary

US1322's round-two qa review (RUN-01M7VNR0) found that `project_upgrade.py` --apply writes personas.standard: report whenever a project's config does not set it, and init.py writes no personas.standard. A project initialised at this release, whose own cards were held to the standard from the start, is therefore moved to report mode, where its own cards are named rather than refused, by its first later upgrade. The upgrade's dry run lists the write, so it is visible, but US1322 is meant for projects upgrading TO the standard, not ones already on it.

## Steps to Reproduce

Run init.py in an empty fixture, then `project_upgrade.py` --apply: the config gains personas.standard: report though the project never ran without the standard.

## Proposed Fix

Have init.py write personas.standard: block into a new project's config (and its template), so the upgrade finds an explicit setting and leaves it; pin it with an init-then-upgrade test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1322's round-two qa review (RUN-01M7VNR0) found that `project_upgrade.py` --apply writes personas.standard: report whenever a project's config does not set...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run init.py in an empty fixture, then `project_upgrade.py` --apply: the config gains personas.standard: report though the project never ran without the...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have init.py write personas.standard: block into a new project's config (and its template), so the upgrade finds an explicit setting and leaves it; pin it with...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
