# BG1445: lessons.py class-add declares a --phase flag, so the upgrade page's row for critic.py's retired --phase no longer matches and test_lean_upgrade_page_docs is red

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** docs/existing-users.md, tools/tests/test_lean_upgrade_page_docs.py, changelog.d/BG1445.md
> **Evidence:** Run twelve (RUN-01M7E52T) full suite on the gate host before the close; bisected to 8cebc5ae (BG1268) by the live-flag rule in scripts/tests/retired_surface.py:40-67
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:13:57Z

## Summary

BG1268 added `lessons.py class-add --phase`. The upgrade-page test (tools/tests/`test_lean_upgrade_page_docs.py`, via scripts/tests/`retired_surface.flags)` matches a retired flag anywhere only while no shipped parser declares it; once one does, the retired flag must sit beside its retired verb in the same code span. docs/existing-users.md:159 writes `--phase` before `critic.py brief`, so the row stops matching: 'the section maps no replacement for critic.py brief|record|correct|show|supersede --phase'. The full suite at the push boundary is red on it.

## Steps to Reproduce

Run pytest tools/tests/`test_lean_upgrade_page_docs.py` -k `retired_surface` at HEAD: one subtest fails on the critic.py --phase label; at 3d8bad1b it passes.

## Proposed Fix

Rewrite the row's first cell so the retired flag sits beside its verb inside one code span (for example `critic.py brief --phase`, and the same flag on `record`, `correct`, `show` or `supersede`), keeping the replacement cell.

## Acceptance Criteria

- [ ] **AC1** Given HEAD, when the upgrade-page test reads the retired surface, then the critic.py --phase label maps to its replacement row, and lessons.py class-add keeps its --phase flag. Fails on: the subtest red, or the flag renamed to dodge the test.
  - **Verify:** pytest tools/tests/test_lean_upgrade_page_docs.py::UpgradePageTests::test_the_upgrade_page_maps_every_retired_surface

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
