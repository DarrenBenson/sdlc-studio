# CR-0751: Prevent or retire lesson LC-001 (mutant never applied)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M84Z8Z close, 2026-11-24T04:28:49Z

## Summary

The failure class LC-001 (mutant never applied) recurred 2 time(s) after it was recorded in back-to-basics-review, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: Trust a mutation verdict only after the mutant was applied and its test was seen to fail.

Behaviour asked of the agent: Assert the replaced text occurs exactly once, purge `__pycache__`, run the named test and watch it go red, then restore; re-apply any registered or reported mutant before citing its count.

Hits:

- RUN-01M80RTZ on BG1483 (critic:RUN-01M80RTZ): The changelog's and reference-retro.md's "none when a REJECT or a Try item already hit it this run" is pinned only for a REJECT. `test_a_class_the_run_already_hit_gains_no_second_hit` (tests/`test_lessons.py`:2220) says in its docstring that it covers "A class a REJECT or a Try item already hit", but it seeds only a `critic:` hit. A mutant whose per-run guard ignores a Try item's `retro:` hit (lessons.py:2262) SURVIVES the same 187 tests. Probed alone with a retro Try item tagged `[LC-001]` and a bug filed in the run citing LC-001: HEAD records one hit, the Try item's, and the mutant records two for one repeat. Add the Try-item case to that test
- RUN-01M84Z8Z on BG1514 (critic:RUN-01M84Z8Z): The AC2 helper's deadline is pinned by no assertion, so its docstring overclaims: with `_batch_once_reported`'s deadline widened by 20 s (`+ 20` on `test_verify_lane_batch.py:417`), AC2's test still passes (1 passed in 27.35 s), so "retry past the deadline", named as a killed mutant at `test_verify_lane_batch.py:433`, survives. The only upper check is a hang: the hand-recorded mutant in BG1514-mutants.json (`if False:` before `self.fail`) is recorded killed though its run produced no verdict in 25 minutes and was stopped by hand, so no red was seen. An upper bound on the never-reporting half's elapsed time would pin both [LC-001]

## Impact

Every lane and review the class reaches: each repeat of LC-001 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-001 describes cannot recur there: RUN-01M80RTZ on BG1483; RUN-01M84Z8Z on BG1514.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-001 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | sdlc-studio | Raised |
