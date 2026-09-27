# BG0806: TSD staleness is never judged in a consuming project and reports a false reason on every sprint plan

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_tsd_staleness.py, changelog.d/BG0806.md
> **Severity:** Medium
> **Points:** 2

## Summary

CR0592 bullet (file line 43) re-measured at f76b70cc: `sprint.tsd_staleness` compares the TSD against the last change to `.claude/skills/sdlc-studio/scripts`, which a consuming project does not have, so on a fresh project and on a clone of a real v4.1 project it returns `known: False` with 'commit times unavailable' though git and both times exist. Every consumer's `sprint plan` prints `TSD staleness UNKNOWN` and records it in sprint-plan.json; a stale TSD is never flagged.

## Steps to Reproduce

In a fresh init project: commit sdlc-studio/tsd.md, then a later commit to src/; python3 -c 'import sprint; print(`sprint.tsd_staleness(`"."))' from the project with scripts on sys.path.

## Proposed Fix

Judge the TSD against the last commit outside sdlc-studio/ in a consuming project; keep the skill-scripts comparison for the skill repository.

## Acceptance Criteria

- [ ] **AC1** Given a consuming project (no skill scripts/ in its tree) whose `sdlc-studio/tsd.md` was committed before a later commit to a path outside `sdlc-studio/`, when `tsd_staleness` runs, then it returns `known: True, stale: True` naming that commit time. Fails on: comparing against `.claude/skills/sdlc-studio/scripts` (HEAD: `known: False` in every consuming project)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tsd_staleness.py::TsdStalenessTests::test_a_consuming_project_with_later_code_reads_stale
- [ ] **AC2** Given the same project whose TSD commit is newer than every commit outside `sdlc-studio/`, then `known: True, stale: False`; and a tree with no git history reports `known: False` naming the missing history. Fails on: counting commits to `sdlc-studio/` artefacts as code, so every backlog commit marks the TSD stale
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_tsd_staleness.py::TsdStalenessTests::test_a_tsd_revised_after_the_code_reads_current

## Notes

First-week: every consumer's first plan prints a false warning. Alternative if capacity binds (1 pt): delete the check in consuming projects and say so, which LC-008 credits. Mint from CR0592 and remove the bullet.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0806) |
