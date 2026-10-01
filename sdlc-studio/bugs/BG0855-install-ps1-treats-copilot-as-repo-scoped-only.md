# BG0855: install.ps1 treats Copilot as repo-scoped only, the Windows twin of BG0852

> **Status:** Open
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD by source (no `pwsh` on this host; `command -v pwsh` is empty): install.ps1:42 `copilot = @{ global = ''`, :101 detects copilot by `gh` or `.github`, :174 `Copilot: reads .github/skills in the repo`, while install.sh:146 maps `copilot:global` to `$HOME/.agents/skills` (BG0852). The Verify runs install.ps1 for real wherever `pwsh` is on PATH (CI) and falls back to pinning the source here, as test_lean_install_ps1_local.py already does for BG0821
> **Severity:** Medium
> **Points:** 2
> **Affects:** install.ps1, tools/tests/test_lean_install_ps1_local.py, changelog.d/BG0855.md
> **Evidence:** install.ps1:42,101,174; goal review round 78 engineering seat
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T08:07:46Z

## Summary

install.ps1 maps copilot's global target to empty (line 42), detects copilot by `gh` or `.github` (line 101), and says Copilot reads only .github/skills (line 174), exactly as install.sh does in BG0852. BG0852 was scoped to install.sh at the 2026-09-30 goal review (round 78, engineering seat) because the build host has no pwsh, so install.ps1 cannot be exercised there; this unit carries the Windows half so the two installers do not diverge silently.

## Steps to Reproduce

Read install.ps1 lines 42, 101 and 174 at 7edb2a2e beside install.sh `target_dir`, `is_detected` and `invoke_note.`

## Proposed Fix

Mirror BG0852's install.sh change in install.ps1 (copilot global to the personal ~/.agents/skills folder, detection by the copilot binary, the detected-not-installed hint), delivered on a host with pwsh.

## Acceptance Criteria

- [ ] **AC1** Given a throwaway HOME and a PATH holding a `copilot` executable and no `gh`, when `install.ps1 -Target copilot -Global -DryRun` runs, then it plans an install into `$HOME/.agents/skills/sdlc-studio`, auto-detection selects copilot by the `copilot` binary, and the post-install note names `~/.agents/skills`. Where `pwsh` is absent, the test pins the same three claims on install.ps1's source (the copilot `global` entry, the detection line, the note) so the selector never passes on a skip. Fails on: HEAD's empty copilot global target, `gh`-based detection and repo-only note
  - **Verify:** pytest tools/tests/test_lean_install_ps1_local.py::InstallPs1CopilotTests::test_auto_selects_a_copilot_personal_folder

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
