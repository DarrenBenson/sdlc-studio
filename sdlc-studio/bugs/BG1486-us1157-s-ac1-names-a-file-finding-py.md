# BG1486: US1157's AC1 names a file_finding.py bug verb that does not exist, so the plan's registry advice reads it as a new verb

> **Status:** Won't Fix
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

- [ ] **AC1** Given US1157's AC1, when it is read beside `file_finding.py --help` and `file_finding.py file --help`, then it states the second creator as `file_finding.py file --type bug --escaped ...`, a command that runs, and `--escaped`, `--shipped-in` and `--escaped-via` are documented on that form. Fails on: the criterion naming a `file_finding.py bug` verb that does not exist, which the plan's registry advice reads as a new verb.
  - **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is a wording preference, not a false statement. US1157 is Done and its AC1 names file_finding.py bug where file --type bug is meant; a wording slip in one closed story, no shipped page. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
