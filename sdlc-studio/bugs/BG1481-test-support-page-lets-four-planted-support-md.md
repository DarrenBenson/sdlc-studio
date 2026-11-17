# BG1481: test_support_page lets four planted SUPPORT.md defects through: a gh skills install line, an install command in prose, and Stack Overflow or IRC named in prose

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_support_page.py, tools/check_links.py, tools/tests/test_check_links.py, changelog.d/BG1481.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1163/7dee924166ea-2b0da0ce.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:23:02Z

## Summary

US1163's QA review (verdict 7dee924166ea-2b0da0ce) killed six of ten mutants against tools/tests/`test_support_page.py.` Survivors: a `gh skills install` line (a command the install guide gives, so SUPPORT.md could drift from it), an install command written in plain prose rather than a code block, and Stack Overflow or IRC named as a channel in prose. Also pre-existing: `check_root_docs` reports only missing Markdown links, so a missing .py or .yml link from a root doc is not caught (every link SUPPORT.md gives today is Markdown).

## Steps to Reproduce

Plant each of the four edits in SUPPORT.md and run pytest tools/tests/`test_support_page.py`: each passes.

## Proposed Fix

Assert SUPPORT.md names no install command anywhere (code block or prose) and no channel outside the repository's issues and security policy; extend `check_root_docs` to non-Markdown relative links.

## Acceptance Criteria

- [ ] **AC1** Given a copy of SUPPORT.md with a `gh skills install` line planted in a code block, and another with an install command written in plain prose, when the support page check reads each copy, then each is reported as an install command the page must not give. Fails on: either planted copy passing.
  - **Verify:** pytest tools/tests/test_support_page.py::SupportPageTests::test_an_install_command_anywhere_is_reported
- [ ] **AC2** Given a copy of SUPPORT.md naming Stack Overflow, and another naming IRC, as a channel in prose, when the check reads each copy, then each is reported as a channel outside the repository's issues and security policy; the page as committed reports nothing. Fails on: a channel named in prose passing, or the real page reported.
  - **Verify:** pytest tools/tests/test_support_page.py::SupportPageTests::test_a_channel_named_in_prose_is_reported
- [ ] **AC3** Given a root doc with a relative link to a .py or .yml file that does not exist, and one to such a file that does, when `check_root_docs` runs, then the first is reported as file missing and the second is not. Fails on: only Markdown link targets being checked.
  - **Verify:** pytest tools/tests/test_check_links.py::RootDocsTests::test_a_missing_non_markdown_link_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
