# BG1598: README install table labels the GitHub Copilot row 'Copilot' because test_install_copilot_global.py pins that exact label, so the README and docs/harnesses.md name the harness differently

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_install_copilot_global.py, tools/tests/test_readme_front_door.py, README.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py, changelog.d/BG1598.md
> **Evidence:** US1318 builder hand-back, 2026-11-18; sdlc-studio/reviews/verdicts/US1321/19ef1a51a344-e3f271af.txt.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:45:07Z

## Summary

US1318's builder kept the README install row as '| Copilot |' because tools/tests/`test_install_copilot_global.py` (outside the unit's Affects) requires that exact row text; docs/harnesses.md and CR0742 call the harness GitHub Copilot. Also from US1321's round-two review: no test pins the NOT MEASURED skip in `sprint_report.py`'s `_NO_MODEL` (a mutant dropping it survives), though no shipped report carries that value.

US1318's qa review (sdlc-studio/reviews/verdicts/US1318/2f7a9eec5748-9aed238e.txt) adds that tools/tests/test_readme_front_door.py pins the short label too (TABLE_ROWS), so the relabel meets a second pin; and that the same test checks an invocation cell only for being non-empty, accepts any backticked span on docs/INSTALL.md or docs/harnesses.md as a verification command's backing, counts a second table as a harness table only when it uses one of the six labels, and pins the 1,500-word limit by the live assertion alone.

## Steps to Reproduce

Rename the README row to '| GitHub Copilot |' and run tools/tests/`test_install_copilot_global.py`: it fails on the label alone.

## Proposed Fix

Have the test match the row by its install target or a label set, then relabel the README row GitHub Copilot; add a fixture whose Cost model figure reads NOT MEASURED.

## Acceptance Criteria

- [ ] **AC1** Given the README install table with its Copilot row labelled `GitHub Copilot`, when `test_install_copilot_global` and `test_readme_front_door` run, then both pass, matching the row by label set (`Copilot` or `GitHub Copilot`) or by its `copilot` target. Fails on: the install test's `^\|\s*Copilot\s*\|` regex and `TABLE_ROWS` failing on the label alone (reproduced by reading both pins at HEAD).
  - **Verify:** pytest tools/tests/test_install_copilot_global.py::CopilotGlobalTests::test_docs_do_not_call_copilot_repo_scoped
- [ ] **AC2** Given README.md, when its install table is read, then the Copilot row's first cell is `GitHub Copilot`, the name docs/harnesses.md uses. Fails on: the row reading `| Copilot |` (README.md line 95).
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_harness_table_is_alphabetical_with_a_verification_command
- [ ] **AC3** Given a report whose Cost model figure reads `NOT MEASURED`, when the evidence page row is built, then the models cell does not name `NOT MEASURED` as a model. Fails on: a mutant dropping `NOT_MEASURED` from `_NO_MODEL` (sprint_report.py line 6821) surviving every test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_page.py::EvidencePageTests::test_a_not_measured_model_figure_names_no_model

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at HEAD (README line 95 reads Copilot, pinned by the install test regex and TABLE_ROWS); sprint_report.py added to Affects for the NOT MEASURED mutant; the front-door test's looser checks the Summary lists are left to a separate filing, not this unit's criteria |
