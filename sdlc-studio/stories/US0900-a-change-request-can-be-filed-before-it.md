# US0900: A change request can be filed before it is sized

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** developer capturing a request mid-sprint
**I want** to file a change request with no size or footprint yet
**So that** a request is captured when it is noticed and sized by `refine`, where that judgement belongs, instead of being refused or given an invented size

## Acceptance Criteria

- **AC1:** Given `file_finding.py file --type cr` with a title, summary and priority but no `--size` and no `--affects`, when it runs, then the CR is written and indexed and it exits 0; `artifact.py new --type cr` with the same fields behaves the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py::CrFilingTests::test_an_unsized_cr_is_filed_by_both_creators
- **AC2:** Given a bug with no `--points` or no `--affects`, then both creators still refuse it before an id is allocated - bugs keep the refusal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_cr_filing.py::CrFilingTests::test_an_unsized_bug_is_still_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
