# BG0682: artifact.py revision writes a bare _identifier into the Revision History, which markdownlint refuses as MD037

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
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

- [ ] **AC1** The behaviour described is corrected: A revision note naming an identifier such as `_brief_key` or `_awaits_signoff` is written verbatim into a markdown table row, where two such tokens read as...
- [ ] **AC2** The proposed fix lands, pinned by a test: Wrap bare underscore-bearing identifiers in code spans (outside existing spans) when writing the note, or escape the underscores; pin with a note carrying two...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
