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

- [ ] **AC1** The behaviour described is corrected: Run fifteen's US1172 QA seat found US1058 at Status Ready while the PRD row that names it reads Complete.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: grep Status sdlc-studio/stories/US1058-*.md (Ready); BG1460 is Fixed; the PRD row naming US1058 says Complete.
- [ ] **AC3** The proposed fix lands, pinned by a test: Move a story carried at the review cap to a terminal status that names the carrying bug when that bug is Fixed (or Superseded by it at the carry), and have...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
