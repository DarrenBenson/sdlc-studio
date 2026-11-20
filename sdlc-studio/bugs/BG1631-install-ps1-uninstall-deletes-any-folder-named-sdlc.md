# BG1631: install.ps1 -Uninstall deletes any folder named sdlc-studio under a target, with none of the guard BG1547 gives install.sh

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.ps1, tools/tests/test_install_uninstall_guard.py, docs/INSTALL.md, changelog.d/BG1631.md
> **Evidence:** install.ps1:231-236 at 4807b774; run nineteen L3 hand-back, 2026-11-19
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T21:55:33Z

## Summary

install.ps1's uninstall branch (around line 231) runs `Remove-Item -Path $dest -Recurse -Force` for every resolved target where `Join-Path <target> sdlc-studio` exists, without checking that the folder is an SDLC Studio install (a SKILL.md naming the skill). A user folder of that name under any target directory is deleted. BG1547 fixes the same fault in install.sh in run nineteen; the PowerShell installer was outside its Affects. Found by the run nineteen installer lane's builder.

## Steps to Reproduce

Create <target>/sdlc-studio holding a file that is not the skill, then run `install.ps1 -Uninstall -Target <that target>`: the folder is removed.

## Proposed Fix

Apply install.sh's BG1547 guard: remove only a folder whose SKILL.md names sdlc-studio, and report and skip any other, with -DryRun saying which it would skip.

## Acceptance Criteria

- [ ] **AC1** Given a target holding a folder named sdlc-studio whose SKILL.md does not name the skill (or has no SKILL.md), when `install.ps1 -Uninstall` runs on that target, then the folder is left in place and reported as skipped, and a folder whose SKILL.md names sdlc-studio is still removed; with no PowerShell on the test host the test reads the uninstall branch and asserts it guards `Remove-Item` on that SKILL.md check, as install.sh's BG1547 guard does
  - **Verify:** pytest tools/tests/test_install_uninstall_guard.py::InstallPs1UninstallGuardTests::test_ps1_uninstall_removes_only_a_folder_whose_skill_md_names_the_skill
  - **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
