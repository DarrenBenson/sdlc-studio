# BG1042: The push preflight's tests leak SDLC_COVERAGE_PYTHON and leave its REFUSES mark and pytest's class unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_prereqs.py, changelog.d/BG1042.md
> **Evidence:** US1005 round-1 QA verdict in sdlc-studio/reviews/critic-verdicts.md (APPROVE, BLOCKING: none), notes 1-5, each executed by the reviewer in its own checkout at 1916da62.
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T14:56:19Z

## Summary

US1005's QA seat approved with five notes. (1) tools/tests/`test_pre_push_prereqs.py` never clears `SDLC_COVERAGE_PYTHON`, and `hook._git` copies os.environ, so with that documented operator variable exported as a path that does not run, three of five tests go red on correct code; the sibling `test_gate_prereqs.py` pops it. (2) AC2's test hides PyYAML at the tag where AC2's Given says coverage, and asserts neither the install route nor the bypass. (3) A crash of the check (a non-UTF-8 requirements-dev.txt raises UnicodeDecodeError, exit 1) is reported as a refusal 'marked REFUSES above' when no line is so marked. (4) No test pins the REFUSES label: a mutant that prints every --refusing line as 'note' survives both modules. (5) No test pins pytest's REFUSES class: a mutant reclassifying it as a note survives.

## Steps to Reproduce

Export `SDLC_COVERAGE_PYTHON`=/nonexistent/python3 and run pytest tools/tests/`test_pre_push_prereqs.py`: 3 failed, 2 passed on correct code.

## Proposed Fix

Set `SDLC_COVERAGE_PYTHON` to empty in the module's push env. Hide coverage and PyYAML together in the tag test and assert Install and the bypass. Have the hook tell a check that could not run (a traceback, no REFUSES line) from a refusal. Assert the coverage line carries REFUSES, and that a missing pytest refuses.

## Acceptance Criteria

- [ ] **AC1** Given `SDLC_COVERAGE_PYTHON` exported as a path that does not run, when `test_pre_push_prereqs.py` runs on the shipped hook, then every test passes.
  - **Verify:** shell SDLC_COVERAGE_PYTHON=/nonexistent/python3 python3 -m pytest -q -p no:cacheprovider tools/tests/test_pre_push_prereqs.py
- [ ] **AC2** Given a check that exits 1 without printing a REFUSES line, when a push runs the hook, then the hook says the check could not run rather than naming prerequisites marked REFUSES.
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_check_that_could_not_run_is_not_called_a_refusal
- [ ] **AC3** A push missing coverage prints that prerequisite on a REFUSES line, and a push missing pytest is refused, each pinned by a test that fails when the line is printed as `note`
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_coverage_and_pytest_are_marked_refuses
- [ ] **AC4** The tag-push test hides coverage and PyYAML together and asserts the install route and the bypass the refusal names
  - **Verify:** pytest tools/tests/test_pre_push_prereqs.py::PushPrerequisiteTests::test_a_tag_push_names_the_install_route_and_the_bypass

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
