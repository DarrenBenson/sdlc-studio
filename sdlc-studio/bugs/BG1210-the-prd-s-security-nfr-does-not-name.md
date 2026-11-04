# BG1210: The PRD's Security NFR does not name meter_cursor.py, which US0989 made reach the network, so the PRD refresh test fails at push

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, changelog.d/BG1210.md
> **Evidence:** BG1160/BG1114 builder report, 2026-11-04; the test fails at 22662d86.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T16:25:55Z

## Summary

2026-11-04, found by the BG1160 lane's hook runs (run five). US0989 added lib/`meter_cursor.py`, which calls the Cursor cloud usage API. tools/tests/`test_lean_prd_refresh.py`::PrdRulesTests::`test_rules_nfrs_and_cost_model_match_the_code` requires the PRD's Security NFR to name every script whose source reaches the network, and fails with 'the Security NFR does not name `meter_cursor.py`, whose source reaches the network'. No commit hook selected that test, so it fails first at the push gate.

## Steps to Reproduce

1. `python3 -m pytest -q tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_rules_nfrs_and_cost_model_match_the_code`.

## Proposed Fix

Add the Cursor usage call to the Security NFR's list of outbound paths, with when it runs, its timeout, its redirect rule and how the key travels.

## Acceptance Criteria

- [ ] **AC1** The PRD's Security NFR names `meter_cursor.py` and the call it makes, and the PRD refresh test passes.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRulesTests::test_rules_nfrs_and_cost_model_match_the_code

## Impact

The push gate and the release gate are red on a doc that no longer lists every network path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
