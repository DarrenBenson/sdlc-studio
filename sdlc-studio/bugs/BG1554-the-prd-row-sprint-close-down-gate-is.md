# BG1554: The PRD row Sprint close-down gate is Complete but credits a Stop-hook installer that does not exist

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1554.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 3, 'v3 and v4 capabilities' table, row 'Sprint close-down gate' (line 311)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:28:41Z

## Summary

Line 311 of sdlc-studio/prd.md, the Sprint close-down gate row marked Complete, says a Stop-hook installer redefines sprint-done as close-gate-green. No installer ships. The skill carries only scripts/hooks/`close_guard.py`, a hook script that the consuming project wires by hand into its own settings file, and nothing in the skill writes that entry. The hook also cannot redefine when a sprint is done: by its own docstring and help/gate.md it is opt-in, blocks one turn end as a reminder, allows on any doubt and never hard-locks. The row's other wording already concedes that the detector is an advisory and not a gate, which leaves the feature name at odds with its description. The row overstates enforcement and gives no signal that would tell Complete from absent.

## Steps to Reproduce

1. Read sdlc-studio/prd.md line 311. The row says a Stop-hook installer redefines sprint-done as close-gate-green, with status Complete.
2. Search the skill's scripts, excluding tests, for `close_guard` and for hooks.Stop.
3. Observed: the only hits are the hook script itself, help/gate.md, reference-retro.md and reference-scripts-verify.md. No script installs the hook.
4. Read the docstring of scripts/hooks/`close_guard.py.` It says the project wires the hook by hand, that it is opt-in, that it allows on any doubt and that it never hard-locks.
5. Expected: the PRD row describes the optional hand-wired reminder that ships.

## Proposed Fix

Reword the row in sdlc-studio/prd.md to say what ships: a close-owed detector, the status and hint nudge, and an optional Stop hook (`close_guard.py)` that a project wires by hand and that reminds once at a turn end without locking. Drop the words installer and redefines sprint-done as close-gate-green, and rename the feature so it no longer calls an advisory a gate, for example Sprint close-down reminder. Add scripts/hooks/`close_guard.py` to the row's source column. Add an assertion to tools/tests/`test_lean_prd_refresh.py` that the PRD names no Stop-hook installer while no script installs one.

## Acceptance Criteria

- [ ] **AC1** Given the Section 3 row of sdlc-studio/prd.md that describes the sprint close-down nudge, when it is read, then it describes an optional Stop hook a project wires by hand that reminds once at a turn end without locking, names scripts/hooks/`close_guard.py` in its source column, and its feature name no longer calls the advisory a gate. Fails on: the row crediting a Stop-hook installer, or saying the hook redefines when a sprint is done.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_the_close_down_row_describes_the_hand_wired_reminder
- [ ] **AC2** Given the shipped scripts, when the test searches them for a writer of a Stop hook entry into a settings file and finds none, then the PRD contains no claim of a Stop-hook installer; with such a writer present the claim is allowed. Fails on: the PRD naming an installer while no script installs the hook.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_no_stop_hook_installer_is_claimed_while_none_ships

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
