# BG1342: sprint.py plan --write --format json prints its run-opening lines on stdout before the JSON

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1342.md
> **Evidence:** RUN-01M77177, 2026-11-12: US1149's builder
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:04Z

## Summary

With --format json and --write, the 'wrote sprint plan' and 'opened run' lines go to stdout ahead of the JSON document, so a caller must hunt for the first '{' line.

## Steps to Reproduce

`sprint.py plan --worklist w --write --format json | python3 -m json.tool` fails.

## Proposed Fix

Print the run-opening lines to stderr under --format json.

## Acceptance Criteria

- [ ] **AC1** Given --write --format json, when sprint plan runs, then stdout is one JSON document and the human lines go to stderr. Fails on: any non-JSON line on stdout.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanJsonTests::test_plan_write_json_stdout_is_one_document

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
