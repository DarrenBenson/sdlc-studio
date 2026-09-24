# BG0762: CI's bandit scan fails on the SHA1 fingerprint US0899 added to reconcile settle

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

reconcile.py:3068 (US0899, commit b3d99279) fingerprints the working-tree bytes of each staged path with hashlib.sha1(...) and no usedforsecurity=False. CI's bandit step (-ll) reports B324 High, so the Lint run on main failed for d57161f9 (run 36047510123). No local lane runs bandit, so neither the commit gates nor the pre-push gate saw it. The hash only detects a changed file, so it is not a security use.

## Steps to Reproduce

Run: bandit -r .claude/skills/sdlc-studio/scripts -ll -x '*/tests/*' -q ; it reports B324 at reconcile.py:3068 and exits 1.

## Proposed Fix

Pass usedforsecurity=False to hashlib.sha1 at reconcile.py:3068 (or use hashlib.blake2b), so bandit's -ll scan exits 0; add no new local lane.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reconcile.py:3068 (US0899, commit b3d99279) fingerprints the working-tree bytes of each staged path with hashlib.sha1(...) and no usedforsecurity=False.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run: bandit -r .claude/skills/sdlc-studio/scripts -ll -x '*/tests/*' -q ; it reports B324 at reconcile.py:3068 and exits 1.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pass usedforsecurity=False to hashlib.sha1 at reconcile.py:3068 (or use hashlib.blake2b), so bandit's -ll scan exits 0; add no new local lane.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
