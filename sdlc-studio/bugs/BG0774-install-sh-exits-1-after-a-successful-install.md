# BG0774: install.sh exits 1 after a successful install when the gemini target is chosen without the gemini CLI

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** install.sh
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

- [ ] **AC1** The behaviour described is corrected: install.sh's `native_hint` (line ~181) ends in 'command -v gemini && echo ...', which returns non-zero under set -e when the gemini CLI is not on PATH, so the...
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the hint's probe non-fatal (|| true) and pin it with a test that installs the gemini target with no gemini on PATH.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
