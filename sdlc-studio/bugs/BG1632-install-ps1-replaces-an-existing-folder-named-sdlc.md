# BG1632: install.ps1 replaces an existing folder named sdlc-studio that is not an SDLC Studio install, where install.sh skips it

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.ps1, tools/tests/test_install_atomic.py, docs/INSTALL.md, changelog.d/BG1632.md
> **Evidence:** run nineteen L3 hand-back, 2026-11-19
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T21:56:32Z

## Summary

When a target already holds a folder named sdlc-studio that is not an SDLC Studio install, install.sh reports and skips it, but install.ps1 deletes it and installs in its place, so a Windows user loses that folder's contents. The two installers disagree on a destructive path. Found by the run nineteen installer lane's builder.

## Steps to Reproduce

Create <target>/sdlc-studio holding a file that is not the skill, then run `install.ps1 -Target <that target>`: the folder is replaced; install.sh on the same layout skips it.

## Proposed Fix

Match install.sh: before replacing a destination, require its SKILL.md to name sdlc-studio, and otherwise report and skip it.

## Acceptance Criteria

- [ ] **AC1** Given a target holding a folder named sdlc-studio that is not an SDLC Studio install, when `install.ps1` installs to that target, then it reports and skips the folder rather than removing it, matching install.sh; with no PowerShell on the test host the test reads the install branch and asserts its `Remove-Item` of an existing destination is guarded by the SKILL.md check
  - **Verify:** pytest tools/tests/test_install_atomic.py::InstallPs1ExistingFolderTests::test_ps1_install_skips_an_existing_folder_that_is_not_the_skill
  - **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
