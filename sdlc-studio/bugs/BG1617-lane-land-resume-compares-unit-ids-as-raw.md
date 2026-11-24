# BG1617: lane land --resume compares unit ids as raw strings, a landing stopped at rebase records no commit, and two refusals have no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_resume.py, changelog.d/BG1617.md
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/US1193/7ca5bf96a772-3421324b.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:44Z

## Summary

Non-blocking findings from the qa review of the resumed land (run eighteen): `--resume` matches the kept hand-in's unit ids by raw string, so a differently spelled id (padding, case) is read as a different landing; the land record of a landing stopped at its rebase names no commit, a gap in the criteria's wording; two refusals are untested.

## Steps to Reproduce

Stop a landing at its rebase, then read its land record: no commit is named. Resume with the unit id spelled with different case: the kept hand-in is not matched.

## Proposed Fix

Normalise ids through `sdlc_md` before comparing, record the commit a rebase stopped on, and test both refusals.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from the qa review of the resumed land (run eighteen): `--resume` matches the kept hand-in's unit ids by raw string, so a differently...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Stop a landing at its rebase, then read its land record: no commit is named.
- [ ] **AC3** The proposed fix lands, pinned by a test: Normalise ids through `sdlc_md` before comparing, record the commit a rebase stopped on, and test both refusals.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Resume id compare and untested refusals.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
