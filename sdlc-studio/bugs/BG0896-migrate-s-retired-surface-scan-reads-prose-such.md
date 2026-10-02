# BG0896: migrate's retired-surface scan reads prose such as 'mutation audit' as a retired command because .py is optional

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/retired_surface.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_surface_prose.py
> **Evidence:** US0975 QA review round 2 (RUN-01M3VF2J)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:58Z

## Summary

lib/`retired_surface.derived()` and `consumer_flags()` make .py optional, so ordinary prose (We run a mutation audit, the sprint preflight checklist) is reported as naming a retired command. 12 consuming repos show 0 hits today.

## Steps to Reproduce

1. A consumer doc line: We run a mutation audit every quarter. 2. migrate.py -> needs-a-human names mutation.py audit.

## Proposed Fix

Require .py or a code span around the script name in the consumer scan.

## Acceptance Criteria

- [ ] **AC1** Given a consumer doc holding 'We run a mutation audit every quarter.' and a second line '`mutation.py audit`', when migrate scans the docs, then only the second line is named. Fails on: the current code names both
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired_surface_prose.py::RetiredSurfaceProseTests::test_prose_without_the_script_name_is_not_surface

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
