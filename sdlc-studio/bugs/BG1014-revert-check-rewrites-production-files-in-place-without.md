# BG1014: revert-check rewrites production files in place without declaring a rewrite window, so a commit made while it runs can stage a reverted file

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_revert_check_window.py, changelog.d/BG1014.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** reference-sprint.md, the declared-window rule; verify_ac.py `revert_check` (no window calls); mutation.py `window_path`/`window_records`.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T09:08:45Z

## Summary

reference-sprint.md states that any process rewriting files in place declares a window (`mutation.py window open --owner <who> --paths <...>`), and that the commit gate and pre-commit hook refuse a staged path an open window claims. `verify_ac.revert_check` reverts each production file in a unit's Affects to its base, runs the verifiers, and restores the bytes in a `finally`, but declares no window, so a concurrent commit (a lane's, or the orchestrator's paperwork) can stage the reverted bytes, the incident the window exists for. Confirmed by the code path at d327d5d0 (no window call in `revert_check)`; found by the G7 breakdown and its panel review (D0355), which recommends shipping it with BG1009.

## Steps to Reproduce

Run `verify_ac.py revert-check --unit <id>` on a unit with a slow verifier; while it runs, `git add` the unit's production file and commit: the reverted bytes are committed and no window was open to refuse them.

## Proposed Fix

Open a window claiming exactly the reverted paths before the first write, owned by revert-check, and close it in the same `finally` that restores the bytes; refuse to start when another owner's open window claims any of those paths.

## Acceptance Criteria

- [ ] **AC1** While revert-check holds a unit's production files reverted, an open window claims exactly those paths, so the commit gate refuses staging any of them, and the window is closed when the bytes are restored
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_window.py::RevertCheckWindowTests::test_reverted_paths_are_claimed_while_reverted
- [ ] **AC2** revert-check refuses to start when another owner's open window claims a path it would revert
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_window.py::RevertCheckWindowTests::test_another_owners_window_refuses_the_start
- [ ] **AC3** A SIGTERM delivered while revert-check holds files reverted restores the bytes and closes its window
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_revert_check_window.py::RevertCheckWindowTests::test_sigterm_restores_and_closes_the_window

## Triage notes (from the G7 breakdown, D0355)

- `mutation.open_window` refuses whenever any window is held (mutation.py:693-706), which is wider than AC2's "a window that claims a path it would revert": decide whether revert-check narrows it or states the wider refusal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | AC3 added from the G7 panel review (D0355); a note on open_window's wider refusal |
