# BG1553: The PRD Environment Variables table omits variables the PRD itself relies on, including the one secret the skill sends

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1553.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 9 Environment Variables, lines 643-650, against Section 3 line 325 and Section 5 lines 522-533
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:35Z

## Summary

Section 9 of sdlc-studio/prd.md lists six environment variables at lines 643 to 650. The PRD elsewhere relies on four more that are absent from the table: `SDLC_STUDIO_HARNESS`, which selects the token meter (line 325), and `CURSOR_API_KEY`, `SDLC_STUDIO_CURSOR_AGENT_ID` and `SDLC_STUDIO_CURSOR_API` (lines 522 to 533), of which the first is a bearer secret and the last overrides a network endpoint. The shipped scripts also read operator-facing variables the PRD never mentions, among them `SDLC_STUDIO_TRANSCRIPTS`, `SDLC_VERIFY_TIMEOUT`, `SDLC_VERIFY_BATCH_TIMEOUT`, `SDLC_VERIFY_WORKERS` and `SDLC_COVERAGE_PYTHON`. CR0285, now Complete, treated four omitted variables in this same table as a defect, so the table is meant to be whole and has fallen behind since the Cursor meter landed. A reader using the PRD as a migration blueprint takes the table as the boundary and misses the cost meter and network override variables.

## Steps to Reproduce

1. Read sdlc-studio/prd.md lines 643 to 650. The table lists `CLAUDE_SKILL_DIR`, `SDLC_AUTHOR`, `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION`, `SDLC_DEBUG` and `SDLC_STUDIO_REQUIRE_CHECKSUM.`
2. Read line 325 and lines 522 to 533 of the same file. They name `SDLC_STUDIO_HARNESS`, `CURSOR_API_KEY`, `SDLC_STUDIO_CURSOR_AGENT_ID` and `SDLC_STUDIO_CURSOR_API` as behaviour-bearing.
3. Search the shipped scripts and their lib folder for names starting `SDLC_` or `CURSOR_.`
4. Observed: the four variables from step 2 and several more are read by the scripts and absent from the table.
5. Expected: every environment variable the shipped scripts read, or the PRD names, has a row.

## Proposed Fix

Add a row to the Section 9 table for each variable the shipped scripts read and an operator may set, starting with the four the PRD already names, and mark `CURSOR_API_KEY` as a secret and `SDLC_STUDIO_CURSOR_API` as a network endpoint override. Keep the `CLAUDE_SKILL_DIR` row but say it is set by the harness and used in the documented commands, not read by a script. Add a test to tools/tests/`test_lean_prd_refresh.py` that collects the variable names the scripts read and fails when one has no row, so the table cannot fall behind again.

## Acceptance Criteria

- [ ] **AC1** Given the Section 9 Environment Variables table of sdlc-studio/prd.md, when the test collects every environment variable name the shipped scripts and their lib folder read, then each one has a row in the table, including `SDLC_STUDIO_HARNESS`, `CURSOR_API_KEY`, `SDLC_STUDIO_CURSOR_AGENT_ID` and `SDLC_STUDIO_CURSOR_API`. Fails on: a variable a shipped script reads having no row, which is how the table fell behind the Cursor meter.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdEnvironmentVariablesTests::test_every_variable_the_scripts_read_has_a_row
- [ ] **AC2** Given the same table, when the rows for `CURSOR_API_KEY` and `SDLC_STUDIO_CURSOR_API` are read, then the first is marked as a secret and the second as a network endpoint override, and the `CLAUDE_SKILL_DIR` row says the harness sets it and no script reads it. Fails on: the one secret the skill sends being listed as an ordinary setting, or a row claiming a script reads a variable none does.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdEnvironmentVariablesTests::test_the_secret_and_the_endpoint_override_are_marked
- [ ] **AC3** Given a copy of the PRD with one variable's row removed, when the same collector runs over it, then it names the missing variable; and a row naming a variable no script reads and the PRD does not mark as harness-set is reported too. Fails on: a collector that passes whatever the table holds.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdEnvironmentVariablesTests::test_a_dropped_row_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
