# BG0089: verify_ac run --root mixes roots: story discovery and report are cwd-relative, verifier cwd and history are root-relative

> **Status:** Fixed
> **Verification depth:** functional (red-then-green: --dir/--report resolve against repo_root; run from a foreign cwd writes the report the Done gate reads; suite 1519)
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

rc-verdict: post-v4 (manifests whenever cwd != root; normal in-repo use unaffected). --dir defaults to 'sdlc-studio/stories' resolved against the CWD (verify_ac.py:984, used bare at :686/:693) and --report is cwd-relative (:1004,:737-740), while the verifier working dir and history use repo_root (:680,:741). Run from outside the repo with --root, the tool verifies the cwd's stories (or none), writes the report under cwd, and appends history under root. Every report consumer is root-relative: the story Done gate (transition.py:28,:124), audit.py:110, status.py:182, review_prep.py:169 - so the gate reads a root report such a run never wrote. Adversarially verified (RV0007); sibling scripts honour --root-from-outside (github_sync._state_path, :62-65).

## Steps to Reproduce

From a directory outside the repo: verify_ac.py run --root /path/to/repo -> 'no stories found' (or the cwd's stories); report lands under cwd; transition to Done under --root reads the stale/absent root report.

## Proposed Fix

Resolve --dir and --report defaults against repo_root.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
