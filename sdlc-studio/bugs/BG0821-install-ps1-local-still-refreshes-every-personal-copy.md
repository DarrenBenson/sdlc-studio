# BG0821: install.ps1 -Local still refreshes every personal copy of the skill, the defect BG0809 fixed only in install.sh

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.ps1, install.sh, docs/INSTALL.md, .claude/skills/sdlc-studio/help/skill-update.md, tools/tests/test_lean_install_ps1_local.py, changelog.d/BG0821.md
> **Evidence:** BG0809 builder hand-back (followups line 58); HEAD 7e53a438: install.ps1 lines ~288-296 sweep both scopes; `git show c1e1f780 --stat` touches install.sh only
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:24:03Z

## Summary

BG0809 (c1e1f780) made `install.sh --local` sweep the local scope only and warn when a personal copy shadows the project one. `install.ps1` was not touched: its sweep still iterates `foreach ($sweepScope in @('global', 'local'))` under `-Local`, so pinning a version in one project on Windows rewrites `~\.claude\skills\sdlc-studio` and every other personal copy, moving each project that loads them. Its builder also left docs/INSTALL.md (the stale-copy sweep bullet) and help/skill-update.md:32 describing the old sweep, and noted that the shadow warning fires on itself when the personal and project paths are the same directory.

## Steps to Reproduce

Read install.ps1's sweep block under -Local; compare with install.sh after c1e1f780.

## Proposed Fix

Mirror BG0809 in install.ps1: under -Local sweep the local scope only and warn, naming both paths and versions, when a personal copy shadows the project copy; skip the warning when the two resolve to one directory (both installers); reword the INSTALL.md sweep bullet and help/skill-update.md:32.

## Acceptance Criteria

- [ ] **AC1** Given install.ps1 run with -Local, then its sweep reads only local-scope directories. Fails on: HEAD, which sweeps global and local
  - **Verify:** pytest tools/tests/test_lean_install_ps1_local.py::InstallPs1LocalTests::test_local_sweeps_the_local_scope_only
- [ ] **AC2** Given personal and project skill paths that resolve to the same directory, when either installer runs --local, then no shadow warning is printed. Fails on: the warning firing on itself
  - **Verify:** pytest tools/tests/test_lean_install_ps1_local.py::InstallPs1LocalTests::test_no_shadow_warning_for_one_directory

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
