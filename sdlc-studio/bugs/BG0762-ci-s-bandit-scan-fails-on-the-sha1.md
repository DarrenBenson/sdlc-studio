# BG0762: CI's bandit scan fails on the SHA1 fingerprint US0899 added to reconcile settle

> **Status:** Fixed
> **Verification depth:** functional (CI's bandit command with its exact flags exits 1 at HEAD and 0 with the fix; the settle fingerprint still changes with the bytes; four mutants killed by the QA reviewer)
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_settle_fingerprint.py, changelog.d/BG0762.md
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

reconcile.py:3068 (US0899, commit b3d99279) fingerprints the working-tree bytes of each staged path with hashlib.sha1(...) and no usedforsecurity=False. CI's bandit step (-ll) reports B324 High, so the Lint run on main failed for d57161f9 (run 36047510123). No local lane runs bandit, so neither the commit gates nor the pre-push gate saw it. The hash only detects a changed file, so it is not a security use.

## Steps to Reproduce

Run: bandit -r .claude/skills/sdlc-studio/scripts -ll -x '*/tests/*' -q ; it reports B324 at reconcile.py:3068 and exits 1.

Re-run at 65cdf1ca on 2026-09-25 through `uvx bandit` (1.9.4, the CI invocation): exit 1, one High, `B324 ... reconcile.py:3068:23`, the only High in the scan. The local `~/.local/bin/bandit` shim has no module behind it, so bandit cannot run here except through `uvx`.

## Proposed Fix

Pass usedforsecurity=False to hashlib.sha1 in `reconcile._unstaged` (or use hashlib.blake2b), so bandit's -ll scan exits 0; add no new local lane.

## Acceptance Criteria

- [ ] **AC1** Given `reconcile._unstaged`, when its source is parsed, then every hashlib call in it either constructs a hash bandit's B324 does not flag or passes `usedforsecurity=False`. Fails on: HEAD's bare `hashlib.sha1(data)`; the same weak hash spelt `hashlib.new("sha1", data)`, which B324 also flags.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_settle_fingerprint.py::SettleFingerprintTests::test_the_unstaged_fingerprint_is_not_a_weak_security_hash
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a fixture repository with a staged file, when its working-tree bytes are edited after staging, then `_unstaged` reports a different fingerprint for it, and the same fingerprint when the bytes are unchanged, so `settle` still leaves the author's unstaged edit alone. Fails on: a misplaced argument that hashes nothing (`hashlib.sha1(usedforsecurity=False).hexdigest()`), or hashing the path instead of the bytes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_settle_fingerprint.py::SettleFingerprintTests::test_the_fingerprint_still_changes_with_the_bytes
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (`uvx bandit` at 65cdf1ca exits 1 on B324 at reconcile.py:3068); criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each naming the wrong fix it fails on; Affects narrowed to the fix and its test; 1 point stands |
