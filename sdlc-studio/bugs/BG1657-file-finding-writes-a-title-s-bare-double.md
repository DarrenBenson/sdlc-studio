# BG1657: file_finding writes a title's bare double asterisk unescaped into the artefact and its index row, which markdownlint refuses

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py, changelog.d/BG1657.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:51:28Z

## Summary

In run twenty (RUN-01M7VNR0), BG1651's title held a bare glob double asterisk. `file_finding.py` wrote it unescaped into the bug's heading, body and bugs/_index.md row, markdownlint reported MD037 (spaces inside emphasis), and the next unrelated commit's markdown lane refused the tree until it was code-spanned by hand.

## Steps to Reproduce

File a bug whose title and summary contain a bare double asterisk between spaces, then run markdownlint on the bug file and sdlc-studio/bugs/_index.md: MD037 errors.

## Proposed Fix

Code-span (or escape) a bare emphasis marker in the title, summary, steps and fix the filer writes, as it already refuses an odd backtick count.

## Acceptance Criteria

- [ ] **AC1** Given a bug filed with a title and summary holding a bare ` ** ` between spaces, when `file_finding.py` writes it, then the H1, the body and the `bugs/_index.md` row hold the marker code-spanned or escaped, and markdownlint passes on both files. Fails on: `_md_safe` leaves `**` as written, so MD037 refuses the bug file and the index.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py::TitleMarkdownTests::test_a_bare_double_asterisk_in_the_title_passes_markdownlint_in_file_and_index
- [ ] **AC2** Given a summary, steps and fix each holding a bare ` ** `, when the bug is filed, then none holds an unescaped `**` outside a code span. Fails on: only the title path is safed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py::TitleMarkdownTests::test_a_bare_double_asterisk_in_summary_steps_and_fix_is_safed
- [ ] **AC3** Given a real `**bold**` pair, a `**Field:**` declaration line and a marker already in a code span, when filed, then each is written as given (the controls beside AC1). Fails on: a fix that escapes every asterisk pair.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py::TitleMarkdownTests::test_real_bold_a_field_declaration_and_a_spanned_marker_are_kept

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: executable criteria for the title and index, the body fields and the controls that real bold and field lines are kept; the test lives beside the existing title markdownlint tests |
