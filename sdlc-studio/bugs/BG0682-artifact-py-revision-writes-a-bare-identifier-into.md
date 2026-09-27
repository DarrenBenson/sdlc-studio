# BG0682: artifact.py revision writes a bare _identifier into the Revision History, which markdownlint refuses as MD037

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG0682.md
> **Evidence:** RUN-01M2JA6J 2026-09-15: BG0666, BG0667, BG0672, US0626, US0823 revision rows each needed a hand fix.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A revision note naming an identifier such as `_brief_key` or `_awaits_signoff` is written verbatim into a markdown table row, where two such tokens read as emphasis and markdownlint refuses the file (MD037). It broke three commit attempts in RUN-01M2JA6J and was hand-repaired each time.

## Steps to Reproduce

1. `artifact.py revision --id <unit> --author x --note 'reads _brief_key and _awaits_signoff'`.
2. `markdownlint` on the file reports MD037 on that row.

## Proposed Fix

Wrap bare underscore-bearing identifiers in code spans (outside existing spans) when writing the note, or escape the underscores; pin with a note carrying two such identifiers.

## Acceptance Criteria

- [ ] **AC1** Given `artifact.py revision --id <unit> --note 'x _check, then _series raises'`, when the Revision History row is written, then both identifiers sit in code spans and markdownlint passes the file (no MD037). Fails on: writing the note verbatim, or code-spanning only the first identifier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::RevisionNoteMarkdownTests::test_bare_underscore_identifiers_are_code_spanned
  - **Verified:** yes (2026-09-27)
- [ ] **AC2** Given a note whose identifier is already in backticks, then the existing span is left as written and only the bare token is wrapped. Fails on: wrapping inside an existing span, which doubles the backticks
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::RevisionNoteMarkdownTests::test_an_existing_code_span_is_left_alone
  - **Verified:** yes (2026-09-27)

## Notes

- - 2026-09-27 (QA triage): reuse `file_finding._md_safe`, not a second escaper (LL0016). The Summary's own example does not trigger MD037; the measured trigger is two underscore identifiers on one line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | QA seat: groomed for Sprint 6 from the triage repro |
