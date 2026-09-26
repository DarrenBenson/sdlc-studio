# BG0774: install.sh exits 1 after a successful install when the gemini target is chosen without the gemini CLI

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** install.sh, tools/tests/test_install_gemini_hint.py, changelog.d/BG0774.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T16:39:23Z

## Summary

install.sh's `native_hint` (line ~181) ends in 'command -v gemini && echo ...', which returns non-zero under set -e when the gemini CLI is not on PATH, so the installer exits 1 after the skill is installed and cuts its Next steps output short. Found by US0943's QA review, pre-existing since f1cb3273 (v1.8.0).

## Steps to Reproduce

1. HOME=<scratch> bash install.sh --from <skill> --no-sweep --target gemini on a machine without the gemini CLI. 2. The skill is installed, then the script exits 1 and the Next steps output stops early.

## Proposed Fix

Make the hint's probe non-fatal (|| true) and pin it with a test that installs the gemini target with no gemini on PATH.

## Acceptance Criteria

- [ ] **AC1** Given a scratch HOME and a PATH with no `gemini` command, when `install.sh --target gemini` installs the skill, then it exits 0 and prints its Next steps output in full. Fails on: a hint probe that returns non-zero under `set -e` when the CLI is absent
  - **Verify:** pytest tools/tests/test_install_gemini_hint.py::InstallGeminiHintTests::test_the_gemini_target_installs_cleanly_without_the_gemini_cli
  - **Verified:** yes (2026-09-26)
- [ ] **AC2** Given the same install with a `gemini` command on PATH, then the hint names it as before. Fails on: silencing the hint entirely to make the exit code clean
  - **Verify:** pytest tools/tests/test_install_gemini_hint.py::InstallGeminiHintTests::test_the_gemini_hint_still_shows_when_the_cli_is_present
  - **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-26 | sdlc | Groomed for v6.0.0-rc.1 (operator ruling: fixed before the rc tag) |
