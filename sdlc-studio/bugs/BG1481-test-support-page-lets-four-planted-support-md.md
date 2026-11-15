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

- [ ] **AC1** The behaviour described is corrected: US1163's QA review (verdict 7dee924166ea-2b0da0ce) killed six of ten mutants against tools/tests/`test_support_page.py.` Survivors: a `gh skills install` line...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Plant each of the four edits in SUPPORT.md and run pytest tools/tests/`test_support_page.py`: each passes.
- [ ] **AC3** The proposed fix lands, pinned by a test: Assert SUPPORT.md names no install command anywhere (code block or prose) and no channel outside the repository's issues and security policy; extend...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
