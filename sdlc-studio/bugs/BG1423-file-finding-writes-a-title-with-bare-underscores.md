# BG1423: file_finding writes a title with bare underscores into the bug heading and index, which markdownlint then refuses as emphasis

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_title_markdown.py, changelog.d/BG1423.md, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: BG1392's filing blocked the record commit
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:49:28Z

## Summary

A finding titled with identifiers such as `_rates`() and `_list` is written as-is into the bug's H1 and the index row, where markdownlint reads the underscores as emphasis (MD037) and refuses the commit carrying it; the filer had to wrap them by hand.

## Steps to Reproduce

File a finding titled 'x: `_rates`() and `_list` differ'; run tools/lint-md.sh: MD037 on the bug and the index.

## Proposed Fix

Code-span underscore-led identifiers in the title, or refuse the title naming the fix.

## Acceptance Criteria

- [ ] **AC1** Given a finding title holding two identifiers that begin with underscores, when it is filed, then the bug file and the index row pass markdownlint. Fails on: an MD037 error on either.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_title_markdown.py::TitleMarkdownTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
