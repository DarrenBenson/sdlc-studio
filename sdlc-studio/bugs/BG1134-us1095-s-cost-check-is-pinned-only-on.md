# BG1134: US1095's cost check is pinned only on the older retro shape, cost-baseline add reports a row the median never uses, and its latest-five window has no test

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_baseline_rules.py, changelog.d/BG1134.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** US1095 QA review, qa-seat-US1095-r1, 2026-10-26, at cada3e15: findings 1-3.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T15:49:58Z

## Summary

US1095's QA review (APPROVE, 2026-10-26). (1) AC3's fixture retro (`test_close_cost_regression.py`:59) has no Keep/Stop/Try section, so the Keep/Stop/Try branch at retro.py:713, the shape templates/reviews/retro.md gives every new retro, is unreached: deleting its cost check passes all 7 tests (the shipped code is right when run). (2) `retro.py cost-baseline add` exits 0 and says 'recorded' for a retro whose VELOCITY row already carries a Priced/pt figure, though the VELOCITY row wins (retro.py:2575-2581) and the new row never joins the median; the duplicate check (retro.py:3819) reads only COST-BASELINE.md. (3) No fixture holds more than five priced runs, so taking all runs or the oldest five at retro.py:2613 passes.

## Steps to Reproduce

Delete the cost check in the Keep/Stop/Try branch and run the module: green. Seed a retro whose VELOCITY row has Priced/pt: 'recorded'.

## Proposed Fix

Add a Keep/Stop/Try retro case to RetroCostCauseTests; make cost-baseline add refuse, naming the VELOCITY row, when that row already carries a priced figure; add a six-run fixture pinning the latest five.

## Acceptance Criteria

- [ ] **AC1** Given a Keep/Stop/Try retro for a run carrying a cost issue and no `## Cost` section, then `retro.py validate` refuses it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_baseline_rules.py::CostBaselineRulesTests::test_a_keep_stop_try_retro_must_name_the_cause
- [ ] **AC2** Given a retro whose VELOCITY row carries a Priced/pt figure, when `cost-baseline add` runs for it, then it refuses naming that row and writes nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_baseline_rules.py::CostBaselineRulesTests::test_a_retro_with_a_priced_velocity_row_is_not_seeded
- [ ] **AC3** Given six priced runs before this one, then the median is taken over the latest five
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_baseline_rules.py::CostBaselineRulesTests::test_the_median_reads_the_latest_five

## Impact

The cost check can regress on the retro shape every new run writes, and an operator can seed a row that does nothing while being told it was recorded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
