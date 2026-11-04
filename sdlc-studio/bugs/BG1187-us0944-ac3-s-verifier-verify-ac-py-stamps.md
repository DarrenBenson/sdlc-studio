# BG1187: US0944 AC3's verifier, `verify_ac.py stamps --bugs`, takes 323 s here at load 1, past the release gate's 300 s default ceiling

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1187.md
> **Evidence:** US1112 builder report: US0944::AC3 red as a timeout in the release verify lane at 300 s, 323 s alone at load 1.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T03:24:29Z

## Summary

2026-11-03, US1112's build (run five). Run five's done-check is one `gate.py --release` passing first time at the default 300 s per-verifier ceiling (D0400). US1112's builder found US0944 AC3 (`shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py stamps --bugs`) takes 323 s on this machine even at load 1, so the criterion reads red as a timeout at the default. BG1183 names two other slow verifiers, not this one. 6.2.0 ran its verify lane at 450 s and then 900 s, which hid it.

## Steps to Reproduce

1. `time python3 .claude/skills/sdlc-studio/scripts/verify_ac.py stamps --bugs` on this repository.
2. It exits 0 in about 323 s, over the 300 s default.

## Proposed Fix

Find where `cmd_stamps` spends its time (a collection per stamp is the likely shape) and resolve every stamp from one collection, so the check finishes well inside 300 s.

## Acceptance Criteria

- [ ] **AC1** `verify_ac.py stamps --bugs` on this repository exits 0 inside 120 s, and still exits 1 naming each stamp that resolves to nothing.
  - **Verify:** shell timeout 120 python3 .claude/skills/sdlc-studio/scripts/verify_ac.py stamps --bugs
  - **Verified:** yes (2026-11-04)

## Impact

The release gate goes red on a passing criterion at its default ceiling, and run five's done-check fails on it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
