# BG1486: US1157's AC1 names a file_finding.py bug verb that does not exist, so the plan's registry advice reads it as a new verb

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/stories/US1157-a-bug-records-that-it-escaped-to-production.md, changelog.d/BG1486.md
> **Evidence:** Run fourteen plan lane builder hand-back (US1169, BG0947), 2026-11-15.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T22:25:46Z

## Summary

US1157 (Done) states its AC1 through `file_finding.py bug --escaped ...`, but `file_finding.py`'s verbs are `file` and `rebuild` (a bug is `file --type bug`). The criterion's prose names a command no one can run, and run fourteen's US1169 registry advice, which reads criteria for new verbs, names `file_finding.py bug` as a new verb on the real backlog. Found by US1169's builder.

## Steps to Reproduce

Read sdlc-studio/stories/US1157-*.md AC1 and run `file_finding.py --help`.

## Proposed Fix

Correct the AC1 text to `file_finding.py file --type bug --escaped ...`, and check the escaped-bug flags are documented on that form.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1157 (Done) states its AC1 through `file_finding.py bug --escaped ...`, but `file_finding.py`'s verbs are `file` and `rebuild` (a bug is `file --type bug`).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read sdlc-studio/stories/US1157-*.md AC1 and run `file_finding.py --help`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Correct the AC1 text to `file_finding.py file --type bug --escaped ...`, and check the escaped-bug flags are documented on that form.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
