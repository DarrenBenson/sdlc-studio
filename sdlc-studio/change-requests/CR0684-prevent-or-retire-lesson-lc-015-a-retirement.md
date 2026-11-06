# CR-0684: Prevent or retire lesson LC-015 (a retirement outruns the deletion)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M6RAP7 close, 2026-11-06T16:12:04Z

## Summary

The failure class LC-015 (a retirement outruns the deletion) recurred 2 time(s) after it was recorded in RUN-01M3VF2J, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: Before retiring a criterion or deleting a test with a removed feature, name the deleted symbol it pins; a test or criterion that pins surviving code is re-pointed, never retired.

Behaviour asked of the agent: US0967 left four Done criteria contradicted and US0978 deleted three tests of surviving code under false retirement notes.

Hits:

- RUN-01M5EM9N on US1096 (critic:RUN-01M5EM9N): US0402 AC3 (sdlc-studio/stories/US0402-*.md:36-42) still reads "product and qa are reported as needing a fresh verdict against goal B while engineering is not" under "Verified: yes". The test it cites (`test_sprint.py`:7856) now asserts a different fixture and rule, and under AC3's own Given the code now reports no seat owed. The supersession is recorded only in the revision-history row (line 54), so a green `verify_ac` run reads against the old text. Mark the criterion itself superseded [LC-015]
- RUN-01M6RAP7 on BG1238 (critic:RUN-01M6RAP7): the Granularity cut drops the man-month-per-hour heuristic sentence ("descriptive context for why day granularity matters - never a target"), which now lives nowhere in the skill, so Done US0193 AC3 (states the granularity rationale with that heuristic as descriptive context, never a target) is contradicted, and its executable Verify `grep "granularity" reference-sprint.md` goes red because only the capitalised "Granularity" survives (reference-sprint.md:573-579, US0193-flow-forecast-defaults-to-day-buckets-and-adds.md:39-40) [LC-015]

## Impact

Every lane and review the class reaches: each repeat of LC-015 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-015 describes cannot recur there: RUN-01M5EM9N on US1096; RUN-01M6RAP7 on BG1238.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-015 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Raised |
