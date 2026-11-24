# BG1739: critic.py record refuses a finding whose bare URL is followed by an escaped semicolon

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_filing_markdown_safe_title.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** run twenty-five, BG1073 qa review rounds one and two
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson (qa); persona; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T13:35:52Z

## Summary

`file_finding._BARE_URL_RE` (`file_finding.py`:1707) runs to the next space, so in `see https://example.com/a\; next` it takes the backslash into the URL's code span, leaving an odd backtick count, and `critic.py record --issues` refuses the finding. BG1073 fixed the same shape for `www.` addresses; the http(s) pass still has it. Base behaves the same.

## Steps to Reproduce

1. `critic.py record ... --issues '[new] see https://example.com/a\; then more'`. 2. It is refused for odd backticks.

## Proposed Fix

Stop the URL match before a backslash that escapes a semicolon, as the address pass now does, and pin it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `file_finding._BARE_URL_RE` (`file_finding.py`:1707) runs to the next space, so in `see https://example.com/a\; next` it takes the backslash into the URL's...
- [ ] **AC2** The proposed fix lands, pinned by a test: Stop the URL match before a backslash that escapes a semicolon, as the address pass now does, and pin it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | Sam Eriksson (qa) | Filed |
