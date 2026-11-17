# BG1547: install.sh uninstall deletes any folder named sdlc-studio without the identity guard the install paths apply

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.sh, docs/INSTALL.md, tools/tests/test_install_uninstall_guard.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at install.sh uninstall_from() lines 542-547 (`rm -rf "$dest"`), against is_skill_copy() lines 596-599 ('Identity guard: only ever touch a directory that is genuinely this skill')
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:53Z

## Summary

`uninstall_from` in install.sh checks only that the target directory exists and then removes it recursively, reporting it as removed. Every other write path is guarded: `install_to` and `sweep_stale` both refuse to touch a folder of that name that fails `is_skill_copy`, on the stated ground that it is the user's and not the installer's to replace. With `--target all` the uninstall covers every resolved skills directory, global or local. A folder named sdlc-studio that holds something else, the very case the install path protects, is deleted with no warning and exit 0. docs/INSTALL.md does not say that uninstall removes a folder that is not the skill, and no test exercises the flag.

## Steps to Reproduce

1. Point HOME at a scratch directory and create .claude/skills/sdlc-studio under it holding only a notes.txt file, with no SKILL.md.
2. Run install.sh with --from naming this repository's skill folder. It warns that the folder is skipped and not touched, and notes.txt survives.
3. Run install.sh with --uninstall and --target claude.
4. Observed: it prints that the folder was removed and that the uninstall is complete, exit 0, and the folder with notes.txt is gone.
5. Expected: a warning that the folder is not an sdlc-studio copy and was left alone.
6. Positive control: the same uninstall over a real installed copy removes it.

## Proposed Fix

Gate the removal in `uninstall_from` on `is_skill_copy`, allowing an empty folder as `install_to` does. For anything else, warn that the folder holds no sdlc-studio SKILL.md and skip it, and have the closing line say when nothing was removed. Treat a symbolic link by removing the link only, never its target. Add a test that runs the uninstall over a foreign folder, an empty folder and a real copy in a scratch HOME, and state the guard in the uninstall section of docs/INSTALL.md.

## Acceptance Criteria

- [ ] **AC1** Given a scratch HOME whose .claude/skills/sdlc-studio holds only notes.txt and no SKILL.md, when install.sh runs with `--uninstall --target claude`, then it warns that the folder is not an sdlc-studio copy, leaves the folder and notes.txt in place and its closing line says nothing was removed. Fails on: the folder deleted and reported as removed.
  - **Verify:** pytest tools/tests/test_install_uninstall_guard.py::UninstallGuardTests::test_a_foreign_folder_is_left_alone_and_said_so
- [ ] **AC2** Given a real installed copy, and separately an empty folder of that name, when the same uninstall runs, then each is removed and reported as removed. Fails on: the guard refusing the installer's own copy or an empty folder.
  - **Verify:** pytest tools/tests/test_install_uninstall_guard.py::UninstallGuardTests::test_a_real_copy_and_an_empty_folder_are_removed
- [ ] **AC3** Given the target path is a symbolic link to a skill copy elsewhere, when the uninstall runs, then the link is removed and the directory it pointed at is intact. Fails on: the uninstall following the link and deleting its target.
  - **Verify:** pytest tools/tests/test_install_uninstall_guard.py::UninstallGuardTests::test_a_symbolic_link_is_removed_and_its_target_kept
- [ ] **AC4** Given docs/INSTALL.md, when its uninstall section is read, then it states that uninstall removes only a folder that is an sdlc-studio copy or is empty. Fails on: the page silent on the guard.
  - **Verify:** pytest tools/tests/test_install_uninstall_guard.py::UninstallGuardTests::test_the_install_page_states_the_uninstall_guard

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
