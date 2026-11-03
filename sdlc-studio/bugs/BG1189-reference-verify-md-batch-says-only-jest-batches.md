# BG1189: reference-verify.md#batch says only jest batches, but verify_ac has a pytest batch cache that the release lane uses

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-verify.md, changelog.d/BG1189.md
> **Evidence:** reference-verify.md:230-239 against verify_ac.py `pytest_batch_cache`.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T03:24:48Z

## Summary

2026-11-03, US1112's build (run five). `reference-verify.md` lines 230-239 say `reconcile --verify --batch` runs jest once and that pytest and vitest batch caches are a fast-follow. `verify_ac.py` has had `pytest_batch_cache` since before run five, and US1112 made it run on xdist workers under its own ceiling (`SDLC_VERIFY_BATCH_TIMEOUT`) for `gate.py --release`. The page tells a reader the pytest path does not exist.

## Steps to Reproduce

1. `sed -n 230,239p .claude/skills/sdlc-studio/reference-verify.md`.
2. `grep -n 'def pytest_batch_cache' .claude/skills/sdlc-studio/scripts/verify_ac.py`.

## Proposed Fix

Rewrite the section to say which runners batch today, which command uses each, and what falls back to a spawn per criterion.

## Acceptance Criteria

- [ ] **AC1** reference-verify.md#batch names the pytest batch, the command that uses it and its ceiling setting, and no longer calls it a fast-follow.
  - **Verify:** shell ! grep -q 'fast-follow' .claude/skills/sdlc-studio/reference-verify.md && grep -q 'SDLC_VERIFY_BATCH_TIMEOUT' .claude/skills/sdlc-studio/reference-verify.md

## Impact

A consuming project reading the reference believes its pytest criteria spawn one by one and plans its gate budget on that.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
