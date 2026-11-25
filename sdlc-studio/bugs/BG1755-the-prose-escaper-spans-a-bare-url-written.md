# BG1755: The prose escaper spans a bare URL written straight against an author's code span so the two spans touch

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** an independent reviewer's verdict in run twenty-six (RUN-01M87B5M), recorded as non-blocking and pre-existing at the unit's base (BG1304, qa seat, verdict 9a8369b48d4b-53de4086)
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T08:32:49Z

## Summary

After BG1304, the prose escaper never makes its own code span touch an author's. A bare URL written straight against an author's code span is still spanned whole, and that span touches the author's, which renders as one broken span. Pre-existing at the base; about 8% of a 200,000-input fuzz with author spans and URLs.

## Steps to Reproduce

1. File a finding whose title holds an author's code span followed directly by a bare URL.
2. The filed title holds two touching code spans.

## Proposed Fix

Leave a bare URL bare, or set it apart, where spanning it would touch an author's span, as BG1304 did for paths and identifiers.

## Acceptance Criteria

- [ ] **AC1** Given prose whose bare URL sits straight against an author's code span, when the escaper runs, then no span it makes touches the author's span and the author's span is unchanged. Fails on: a URL span touching an author's span.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
