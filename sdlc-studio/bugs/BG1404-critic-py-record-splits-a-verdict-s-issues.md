# BG1404: critic.py record splits a verdict's ISSUES at every semicolon, so a semicolon inside one finding becomes an untagged finding and the record is refused

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py, changelog.d/BG1404.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review upgrade
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:11Z

## Summary

Reviewers write prose with semicolons, and each becomes a separate untagged finding.

## Steps to Reproduce

Record ISSUES: [blocking] a; b.

## Proposed Fix

Split only before a tag.

## Acceptance Criteria

- [ ] **AC1** Given an ISSUES line with a semicolon inside one tagged finding, when `critic.py record` runs, then it is one finding. Fails on: the record refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py::IssuesSemicolonTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
