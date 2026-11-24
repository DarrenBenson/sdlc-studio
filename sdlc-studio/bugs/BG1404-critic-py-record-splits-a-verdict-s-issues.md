# BG1404: critic.py record splits a verdict's ISSUES at every semicolon, so a semicolon inside one finding becomes an untagged finding and the record is refused

> **Status:** Open
> **Ruling:** D0536 (operator, 2026-11-19): narrowed - keep the fail-closed split at a bare semicolon (BG1032); the fix is only that critic.py record's refusal names the \; escape. Re-groom the criteria to that before planning.
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py, changelog.d/BG1404.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review upgrade. Reproduced at cecc9dfe through `critic.main(["record", ...])` in a throwaway project, 2026-11-24.
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:11Z

## Summary

Reviewers write prose with semicolons. `critic.py record` splits ISSUES at a bare semicolon (the fail-closed choice of BG1032, kept by D0536), so the text after a semicolon inside one finding becomes an untagged finding and the record is refused. The escape exists: `\;` keeps a semicolon inside one finding, and the brief's return contract and the `--issues` help both say so. The refusal does not: it lists the untagged piece and the three origin tags, so a reviewer whose finding was split reads it as a missing tag and has no pointer to the escape.

## Steps to Reproduce

1. `critic.py record --unit US0001 --verdict reject --reviewer qa-seat --author eng-seat --issues "[new] a; b"`: exit 2, "record refused: these findings carry no origin", listing `b`, with no mention of `\;`.
2. The same with `--issues "[new] a\; b"`: recorded, one finding `a; b`.

## Proposed Fix

Keep the split. Add one line to the origin refusal in `cmd_record` saying that a piece continuing the finding before it was split at a bare semicolon, and that `\;` keeps a semicolon inside one finding, with the escaped form of the example.

## Acceptance Criteria

- [ ] **AC1** Given `--issues "[new] a; b"`, when `critic.py record` runs, then it exits 2, writes no ledger row, and its refusal names `\;` as the way to keep a semicolon inside one finding. Fails on: the refusal names only the three origin tags, never the escape.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py::IssuesSemicolonTests::test_the_origin_refusal_names_the_escape
- [ ] **AC2** Given a verdict file whose ISSUES line is `[new] a; b`, when `critic.py record --from-verdict <file>` runs, then it exits 2, writes no row, and the refusal names `\;`. Fails on: the same refusal without the escape, on the entry point reviewers use.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py::IssuesSemicolonTests::test_the_from_verdict_refusal_names_the_escape
- [ ] **AC3** Given `--issues "[new] a\; b"`, when `critic.py record` runs, then it records one finding that reads back as `a; b`. Fails on: a fix that changes the split or the escape instead of the message, against D0536 (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_issues_semicolon.py::IssuesSemicolonTests::test_an_escaped_semicolon_keeps_one_finding

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five to D0536: reproduced at cecc9dfe; the escape works and the refusal does not name it; criteria rewritten to the refusal on both entry points plus a guard that the split is kept; Summary, Steps and Proposed Fix narrowed to match; Affects drops test_critic.py; Points stay 1 |
