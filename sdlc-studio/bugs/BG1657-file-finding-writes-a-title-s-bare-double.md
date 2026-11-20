# BG1657: file_finding writes a title's bare double asterisk unescaped into the artefact and its index row, which markdownlint refuses

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
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

- [ ] **AC1** The behaviour described is corrected: In run twenty (RUN-01M7VNR0), BG1651's title held a bare glob double asterisk.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: File a bug whose title and summary contain a bare double asterisk between spaces, then run markdownlint on the bug file and sdlc-studio/bugs/_index.md: MD037...
- [ ] **AC3** The proposed fix lands, pinned by a test: Code-span (or escape) a bare emphasis marker in the title, summary, steps and fix the filer writes, as it already refuses an odd backtick count.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
