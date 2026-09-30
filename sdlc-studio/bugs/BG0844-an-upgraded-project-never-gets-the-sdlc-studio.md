# BG0844: An upgraded project never gets the sdlc-studio/.gitignore that init writes, so gate.py leaves runtime state in git status on every run

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, changelog.d/BG0844.md
> **Evidence:** docs/upgrade-rehearsal-v6.md (US0962), git status after the before-checks on both copies; init.py step 3b writes sdlc-studio/.gitignore, project_upgrade does not; field report 2026-09-29 (v5.0.1 to v6.0.0 upgrade under Copilot CLI): `sdlc-studio/.local/run-state.json` untracked and unignored after `migrate --apply`, which reported only the `.version` bump
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T19:42:41Z

## Summary

US0962 rehearsal (skill 6.0.0-rc.1 at 5e45cbf9): neither project carries `sdlc-studio/.gitignore`, which `init` writes (`.local/`, BG0036), and `migrate --apply` does not add it. On the v4.1 project the first `gate.py` run left `sdlc-studio/.local/gate-cost.json` untracked and unignored; on the v2.4 project `.local/` is committed (runtime caches, verify reports, run state and consult notes) and every `gate.py` run rewrites the tracked `gate-cost.json`. The upgrade commit and every later commit carry derived state or a dirty tree. Tracked `.local/` files need a human (`git rm --cached`); the ignore file is deterministic.

## Steps to Reproduce

Copy a workspace with no sdlc-studio/.gitignore; run `migrate.py --apply` then `gate.py`; `git status --porcelain` shows `sdlc-studio/.local/gate-cost.json`.

## Proposed Fix

Add the `sdlc-studio/.gitignore` seed (the same content init writes, from one shared constant) to project upgrade's deterministic conventions set, written only when absent; when `.local/` already holds tracked files, report them as a needs-a-human item with the `git rm -r --cached sdlc-studio/.local` command, never run it.

## Acceptance Criteria

- [ ] **AC1** Given a fixture workspace with no `sdlc-studio/.gitignore`, when `migrate.py --apply` runs, then `sdlc-studio/.gitignore` exists with the content `init` writes and the dry run lists it as a deterministic upgrade without writing it. Fails on: today's upgrade, which never writes it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RuntimeStateIgnoreTests::test_apply_seeds_the_runtime_state_gitignore
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given a fixture git repository with a tracked file under `sdlc-studio/.local/`, when `migrate.py` runs, then a needs-a-human item names the tracked runtime state and the untracking command, and the file is still tracked afterwards. Fails on: silence, or an upgrade that untracks it for the user
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py::RuntimeStateIgnoreTests::test_tracked_runtime_state_is_reported_not_untracked
  - **Verified:** yes (2026-09-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
