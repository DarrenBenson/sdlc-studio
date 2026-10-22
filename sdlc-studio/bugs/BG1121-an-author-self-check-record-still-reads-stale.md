# BG1121: An author self-check record still reads stale in landing orders the per-file own-change view cannot see through: work recorded before its own commit, a cherry-pick, or another unit's hunk in a file the author also changed

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_survives_a_later_unit.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py, changelog.d/BG1121.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/help/review.md, sdlc-studio/reviews/author-self-checks.md
> **Evidence:** BG1117 QA review round 1, qa-seat-BG1117-r1, at 57a2bb7a: blocking finding 1's cases and the pre-existing US1089 case.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T13:35:46Z

## Summary

BG1117's QA review (round 1, 2026-10-22). BG1117 sets aside other units' later commits per file, stopping at the unit's own newest commit, which handles a record taken after the unit's own commit has landed. It still reads stale when: the author records uncommitted work, another unit lands, then the author's commit lands; another unit commits only its own hunk in a file the author also changed after the record; or the unit's commit is cherry-picked onto a branch. BG1117's own motivating case is one: US1089's recorded digest 9bd14739 is e58c7bcd's content without US1090's AGENTS.md hunk, and it still reads stale with the commit a74e8352. Fixing these needs hunk-level binding (the unit's own diff), not per-file content.

## Steps to Reproduce

Record US1089's self-check against a74e8352 as in run three; check `self_check_gap` on main: stale.

## Proposed Fix

Bind the record to the unit's own change: the diff of its commits against their parents, restricted to Affects, compared hunk by hunk with the current content; or record the patch id of the unit's commits and match it after a cherry-pick.

## Acceptance Criteria

- [ ] **AC1** Given a record of uncommitted work, another unit's commit to a shared file, then the author's own commit, when the unit is briefed under block, then it is admitted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_a_record_before_the_units_commit_survives_a_sibling_landing_first
- [ ] **AC2** Given a record and the unit's commit cherry-picked onto another branch, then the brief there is admitted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_hunk_binding.py::HunkBindingTests::test_a_cherry_picked_commit_keeps_its_record

## Impact

Authors re-record unchanged evidence in these orders, the churn BG1117 set out to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
| 2026-10-22 | sdlc | BG1117 round-2 QA review: help/review.md:48-49, the critic.py comment at 2690-2691 and the self-check log header (critic.py `_SELF_CHECK_HEADER` and author-self-checks.md) still say a record of committed work survives, which a cherry-pick after another unit's commit contradicts; the fix corrects them, and Affects gains the two doc files (critic.py is already declared) |
