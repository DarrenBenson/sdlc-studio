# CR-0683: Fix three run-seven frictions in which a shipped step leaves state the next step refuses: `lane land` checks the self-check hand-in only after it commits, `verify_ac run` in a builder worktree stamps the story file outside the unit's Affects, and `file_finding --parent` leaves the parent RFC's spawned-work cell unsynced

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Bug
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** RFC0062 Phase 3, run seven frictions F1, F2 and F5 (frictions7.txt); orchestration lens: finding 6 (lane land)
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:52Z

## Summary

Run seven (RUN-01M6RAP7). F2: the lane brief's claim inventory names both 'CHANGELOG' and 'changelog.d/<ID>.md'; US1122's builder labelled its 8 fragment claims CHANGELOG, and lane land's self-check record refused after the commit had landed, so no QA brief was written. F5: `verify_ac run` in a builder's worktree stamps the story file, outside the unit's Affects, leaving an unstaged change each builder restored by hand (US1122, US1124, US0987). F1: filing CR0665 to CR0669 with `file_finding --parent RFC0062` left the RFC's spawned-work cell unsynced, so the next commit refused on reconcile drift until `reconcile apply` ran. None is covered by BG1231 (lane land exit codes) or BG1232 (the lane brief's hand-in).

## Impact

Each costs an orchestrator or builder hand-fix per unit or per filing; F2 lands a unit with no QA brief, which an unattended drive loop would carry forward.

## Acceptance Criteria

- [ ] `lane land` validates the hand-in's self-check claims before it commits and refuses with the offending label, leaving no commit, and the lane brief names one label for a fragment claim; a fixture with US1122's CHANGELOG labels is refused before any commit.
- [ ] `verify_ac run` in a lane worktree changes no file outside the unit's Affects: after a fixture run, `git status --porcelain` lists nothing outside them.
- [ ] `file_finding --parent <RFC>` and `artifact.py new --parent <RFC>` each update the parent's spawned-work cell in the same write, so `reconcile --dry-run` reports no drift after filing.

## Recommendation

Move lane land's self-check validation ahead of the commit and give the brief one label; keep verify stamps inside the unit's footprint (in the run state, or staged with the hand-in); sync the parent cell when filing. Saving not grounded by a lens: a few hand-fix calls per affected unit or filing, about four instances in run seven so far. Fix it before the sprint-drive CR, which chains these steps unattended. Risk: none; it moves refusals earlier and removes hand restores.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
| 2026-11-09 | Claude Opus 5.5 | AC3 names `artifact.py new --parent` too: filing CR0689 under RFC0063 left the spawned-work cell unsynced and the commit refused on reconcile drift |
