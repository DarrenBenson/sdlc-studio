# CR-0713: Prevent or retire lesson LC-019 (a push-gate guard the per-commit run skips)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/lessons.jsonl
> **Date:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M7HA6R close, 2026-11-16T09:53:31Z

## Summary

The failure class LC-019 (a push-gate guard the per-commit run skips) recurred 2 time(s) after it was recorded in RUN-01M6RZQZ, while its rule was injected into the work. A rule that is read and repeated anyway needs the path it fails on fixed, not another reading and not one more check. This CR carries the class and its evidence, not a design.

Rule: A test that does not import its subject names it with `# test-census-subject: <path>`, a new or changed CLI subcommand regenerates `reference-scripts-surface.md` with `docgen.py surface`, and a new `sprint.py` verb or sub-verb appears in `help/sprint.md` as a runnable invocation.

Behaviour asked of the agent: Before staging, give a changed script a `build_parser()` and its `sdlc-studio/reviews/command-audit.md` row, and give a new top-level verb a close-checklist row or an entry in `sprint_report.NON_CEREMONY_VERBS`; the push gate refuses each one the commit run let pass.

Hits:

- RUN-01M7GEHM on BG1395 (retro:RETRO0147)
- RUN-01M7HA6R on US1170 (retro:RETRO0148)

## Impact

Every lane and review the class reaches: each repeat of LC-019 has cost a review round, 2 so far.

## Acceptance Criteria

- [ ] The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-019 describes cannot recur there: RUN-01M7GEHM on BG1395; RUN-01M7HA6R on US1170.
- [ ] Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.
- [ ] Once the path is fixed and this CR closes Complete, LC-019 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Raised |
