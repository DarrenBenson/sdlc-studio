# US0907: The backlog holds only the work the lean direction still wants

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/reviews/backlog-sweep-2026-09-24.md, sdlc-studio/decisions.md, sdlc-studio/stories/_index.md, sdlc-studio/bugs/_index.md, sdlc-studio/change-requests/_index.md, sdlc-studio/epics/_index.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py
> **Epic:** EP0262
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer planning the next sprint
**I want** every open item the backlog review ruled superseded, retired or merged closed through the tooling with its reason
**So that** planning reads the 74 items that still matter instead of 327, and nobody re-grooms work the lean process has already replaced

## Acceptance Criteria

- **AC1:** Given the product-seat ruling recorded with `decisions.py rule --seat product` citing sdlc-studio/reviews/backlog-sweep-2026-09-24.md (one row per item: id, verdict, reason), then every item it rules SUPERSEDED, RETIRE or MERGE reads a terminal status of its own type (Superseded, Won't Implement, Won't Fix or Rejected; Superseded for an epic), set by `transition.py`, with a revision row carrying its reason and the ruling id, and a MERGE item names the unit it merged into
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_every_ruled_item_is_terminal_with_its_reason
- **AC2:** Given an item the record rules KEEP-LEAN, KEEP-VALUE or UNSURE, then it carries no revision row citing the sweep ruling - the sweep never touched it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_kept_and_unsure_items_carry_no_sweep_row
- **AC3:** Given BG0709, then it reads Fixed or a later terminal status, citing US0881 AC4 (`tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read`) as the verification of its fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_bg0709_reads_fixed_by_us0881

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
