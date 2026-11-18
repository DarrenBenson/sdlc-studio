# BG1522: The commit gate reuses a selected green suite verdict for a different selection, skipping the second commit's tests

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/gate.py suite_decision(), the off-boundary reuse branch (approx. lines 2896-2925: `recorded != digest` / `return {"run": False, "mode": "reuse" ...}`); written by .githooks/commit-msg lines 504-506 (`--record-suite-verdict ... --verdict-mode selected`); consumed by .githooks/pre-commit lines 483-489
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:08Z

## Summary

In `gate.py`, a green verdict earned by a selected run is keyed only on `surface_hash`, which hashes the working-tree content of every tracked file, and the record holds no list of the modules that ran. Off a boundary, `suite_decision` reuses any green verdict whose hash matches, whatever its mode. When the working tree holds edits to two files and the first commit stages only one, the verdict recorded after that commit already covers the hash of the second file's unstaged edit. Committing the second file then finds the surface unchanged and skips, so the tests that change selects never run against it. Committing several units' files one after another from one working tree is this repository's normal flow, and only the push boundary declines a selected verdict.

## Steps to Reproduce

1. In a throwaway repository lay out a.py, b.py, tests/`test_a.py` and tests/`test_b.py` under .claude/skills/sdlc-studio/scripts, and commit them.
2. Edit both a.py and b.py, breaking b.py so that `test_b` would fail, and stage only a.py.
3. Run gate.py with --suite-decision and --staged: it decides to run and selects `test_a.py` alone.
4. Run gate.py with --record-suite-verdict for HEAD, --status green and --verdict-mode selected, as commit-msg does, then commit a.py.
5. Stage b.py and run gate.py with --suite-decision and --staged again: it prints skip, the tracked surface is unchanged since the selected green verdict, with suite-mode reuse.
6. Positive control: delete the verdict file and repeat step 5: it decides to run and selects `test_b.py.`

## Proposed Fix

Record the selectors that ran with a selected verdict in `record_suite_verdict`, and in the off-boundary reuse branch of `suite_decision` reuse a selected verdict only when the current selection is a subset of the recorded one; a selected verdict with no recorded selectors is never reused for a non-empty selection. A full-mode green keeps its present reuse. Pin the two-file sequence above, with its positive control, in the gate tests.

## Acceptance Criteria

- [ ] **AC1** Given a throwaway repository with edits to a.py and b.py, a selected green verdict recorded after a.py alone was staged and committed, when b.py is staged and `gate.py --suite-decision --staged` runs, then it decides to run and selects `test_b.py`. Fails on: a skip with suite-mode reuse because the tracked surface is unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SuiteVerdictReuseTests::test_a_selected_green_is_not_reused_for_a_different_selection
  - **Verified:** yes (2026-11-18)
- [ ] **AC2** Given a selected green verdict whose recorded selectors include the current selection and an unchanged surface, when `--suite-decision` runs off a boundary, then it reuses the verdict, and a full-mode green keeps its present reuse. Fails on: a fix that ends reuse altogether, so every commit pays the suite again.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SuiteVerdictReuseTests::test_a_selected_green_is_reused_for_a_subset_of_its_selectors
  - **Verified:** yes (2026-11-18)
- [ ] **AC3** Given a selected green verdict that records no selectors, as every record written before this fix does, when `--suite-decision` runs with a non-empty selection, then it decides to run. Fails on: an old record with no selectors read as covering any selection.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SuiteVerdictReuseTests::test_a_selected_green_with_no_recorded_selectors_is_never_reused
  - **Verified:** yes (2026-11-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
