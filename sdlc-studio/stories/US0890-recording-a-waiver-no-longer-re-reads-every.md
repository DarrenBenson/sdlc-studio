# US0890: Recording a waiver no longer re-reads every script

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_decisions_cache.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** developer committing a change to a widely imported script
**I want** the waiver-subject scan to parse the scripts tree once per process instead of on every call
**So that** the tests that record waivers stop spending most of their time re-parsing 72 unchanged scripts, and a hub commit's suite fits the 90-second budget

## Acceptance Criteria

- **AC1:** Given one process that validates or records waivers repeatedly over an unchanged scripts tree, when `waivable_subjects` or `record_waiver` is called ten times, then each script under `scripts/` is parsed at most once in that process (today every call parses all of them, 0.34s a call)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_decisions_cache.py::DecisionsScanCacheTests::test_each_script_is_parsed_at_most_once_per_process
- **AC2:** Given a script whose content changes between two calls (a new `WAIVER_RULE` constant, so its size differs), or a script added or deleted, when the next call runs, then its subject list reflects the change - a cache keyed on file names alone, or held for the life of the process regardless of the tree, fails this
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_decisions_cache.py::DecisionsScanCacheTests::test_a_changed_added_or_deleted_script_is_rescanned
- **AC3:** Given the shipped `decisions.py waive` entry point, when a waiver names an unknown subject it is still refused naming the known subjects, and a declared rule subject is still recorded - the cache changes the cost, never the answer
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_decisions_cache.py::DecisionsScanCacheTests::test_the_waive_cli_answers_are_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
