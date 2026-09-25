# US0907: The backlog holds only the work the lean direction still wants

> **Status:** Done
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

- **AC1:** Given the product-seat ruling recorded with `decisions.py rule --seat product` citing sdlc-studio/reviews/backlog-sweep-2026-09-24.md (one row per item: id, verdict, reason), then every item it rules SUPERSEDED, RETIRE or MERGE reads a terminal status of its own type (Superseded, Won't Implement, Won't Fix or Rejected; for an epic, the close derived from its children, which is Done only when a child was delivered), set by `transition.py`, with a revision row carrying its reason and the ruling id; a MERGE item names the unit it merged into and that unit names it in a `Merged from:` field; and every item it rules DELIVERED reads its type's delivered status (Fixed, Complete, or Done derived for an epic) with the same revision row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_every_ruled_item_is_terminal_with_its_reason
  - **Verified:** yes (2026-09-24)
- **AC2:** Given an item the record rules KEEP-LEAN, KEEP-VALUE or UNSURE, then it carries no revision row citing the sweep ruling - the sweep never changed its status or its history
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_kept_and_unsure_items_carry_no_sweep_row
  - **Verified:** yes (2026-09-24)
- **AC3:** Given BG0709, then it reads Fixed or a later terminal status, citing US0881 AC4 (`tools/tests/test_lean_push.py::PushBoundaryTests::test_a_stale_red_answer_is_re_read`) as the verification of its fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_bg0709_reads_fixed_by_us0881
  - **Verified:** yes (2026-09-24)
- **AC4:** Given an item the record HOLDS under D0264 (superseded only by work that has shipped), then it carries a `Closes with:` field naming the EP0263 stories whose delivery closes it, the same stories the record names
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_held_items_stay_open_naming_their_closing_story
  - **Verified:** yes (2026-09-24)
- **AC5:** Given an item the record HOLDS under D0264, then it reads a non-terminal status until every story its `Closes with:` field names is Done (BG0772)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py::BacklogSweepTests::test_a_hold_closes_only_after_its_story_ships
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
| 2026-09-24 | Claude Opus 5.5 | Review round 1: AC1 reworded from 'Superseded for an epic' to the close derived from an epic's children (EP0171 is Done because it delivered four stories), and names DELIVERED items and a MERGE survivor's Merged-from line; AC4 added for the items D0264 holds open until their EP0263 story ships |
| 2026-09-25 | sdlc-studio BG0772 | BG0772: AC4's non-terminal clause split out as AC5, the conditional hold rule (a held item reads non-terminal until every story its Closes with field names is Done), verified by its own selector because a second Verify line under one criterion is never run (BG0687); AC4 keeps the field checks, its selector and its stamp |
