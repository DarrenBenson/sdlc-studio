# BG0885: critic.py record writes a finding into critic-verdicts.md unescaped, so markdown-shaped text breaks the lint

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M3VF2J paperwork commit refused on US0972's verdict
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T18:37:45Z

## Summary

critic.py record copies --issues text into sdlc-studio/reviews/critic-verdicts.md as raw markdown. A finding quoting a regex such as [A-Z][A-`Z_]`{4,} is read as an undefined reference link (MD052), so the paperwork commit carrying the verdict is refused until the ledger is hand-edited.

## Steps to Reproduce

1. critic.py record --unit X --verdict REJECT ... --issues '[new] the shape [A-Z][A-`Z_]`{4,} matches UNKNOWN'. 2. git commit the ledger -> markdown lane FAIL MD052.

## Proposed Fix

Write each finding's text inside a code span, or escape [ ] and | when recording.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: critic.py record copies --issues text into sdlc-studio/reviews/critic-verdicts.md as raw markdown.
- [ ] **AC2** The proposed fix lands, pinned by a test: Write each finding's text inside a code span, or escape [ ] and | when recording.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
