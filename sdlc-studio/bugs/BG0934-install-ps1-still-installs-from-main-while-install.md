# BG0934: install.ps1 still installs from main while install.sh installs the latest release

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** install.ps1, tools/tests/test_lean_install_ps1_default.py, changelog.d/BG0934.md
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T13:08:05Z

## Summary

The quick start now fetches the latest verified release by default in install.sh, but install.ps1 still defaults to main, so a Windows user gets unreleased code by default and the docs describe two defaults. Found by the v6.1 US0983 build (D0326).

## Steps to Reproduce

1. Read install.sh's and install.ps1's default source. 2. They differ.

## Proposed Fix

Default install.ps1 to the latest release as install.sh does, keeping an explicit main option. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given install.ps1 run with no version argument, then it resolves the latest release as install.sh does, and an explicit main still installs main. Fails on: the current default of main
  - **Verify:** pytest tools/tests/test_lean_install_ps1_default.py::InstallPs1DefaultTests::test_install_ps1_defaults_to_the_latest_release
  - **Verified:** yes (2026-10-03)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
