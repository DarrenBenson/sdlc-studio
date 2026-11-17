# BG1499: US1058 still reads Status Ready though run thirteen carried it at the review cap and BG1460 delivered it, and the PRD row naming it says Complete

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, sdlc-studio/stories/US1058-persona-memory-py-keeps-each-persona-s-evidenced.md, changelog.d/BG1499.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1172 QA verdict 91be561f8170-9c671c7e, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T06:07:01Z

## Summary

Run fifteen's US1172 QA seat found US1058 at Status Ready while the PRD row that names it reads Complete. Run thirteen carried US1058 at the review cap to BG1460, which is Fixed, but nothing moved the story to a terminal status or recorded where its work went, so the backlog counts a delivered story as open work and the PRD and the story disagree.

## Steps to Reproduce

grep Status sdlc-studio/stories/US1058-*.md (Ready); BG1460 is Fixed; the PRD row naming US1058 says Complete.

## Proposed Fix

Move a story carried at the review cap to a terminal status that names the carrying bug when that bug is Fixed (or Superseded by it at the carry), and have reconcile flag a carried story left open after its carrier closes; then settle US1058.

## Acceptance Criteria

- [ ] **AC1** Given a story carried at the review cap to a carry bug, with the bug Fixed and the story still at a non-terminal status, when `reconcile.py` runs, then it reports the story by id, names the carrying bug and gives the transition that settles it. Fails on: a delivered story counted as open work with nothing flagging it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CarriedStoryLeftOpenTests::test_a_carried_story_open_after_its_carrier_is_fixed_is_flagged
- [ ] **AC2** Given the same story while its carry bug is still Open, and a second fixture where the story is already terminal and names the bug, when `reconcile.py` runs, then neither is reported. Fails on: a story flagged while its carrier is still in work, or after it was settled.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::CarriedStoryLeftOpenTests::test_a_story_whose_carrier_is_open_or_that_is_settled_is_not_flagged
- [ ] **AC3** Given this repository's US1058, when its header is read after the fix, then its Status is terminal and names BG1460 as the unit that delivered it, moved with `transition.py`, and the PRD row that names it agrees. Fails on: US1058 left at Ready, or settled by a hand edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
