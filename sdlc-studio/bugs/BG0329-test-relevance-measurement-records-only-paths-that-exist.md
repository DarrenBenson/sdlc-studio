# BG0329: Test-relevance measurement records only paths that exist, so a commit deleting a suite-read file outside the legacy dirs

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The measured test-relevant set is enumerated from files present on disk at commit time, so a staged deletion or rename of a measured file drops it from the set, `is_test_relevant` answers no, and the suites are skipped on exactly the commit that breaks them; measured FILE entries with no covering directory (install.sh, package.json, .markdownlint.json, docs/benchmarks/protocol*.md, sdlc-studio/trd.md, reviews/root-census.md) are silently exempt, falsifying the block's own guarantee 'Neither skips one that was [needed]'.

## Steps to Reproduce

Evidence (`_module_read_paths`'s _record helper, line 1848; `_matches_relevant` lines 1922-1932; hook consumption at .githooks/pre-commit lines 371-378): gate.py:1847-1854 returns early on os.path.exists failure; live --test-relevant run confirms those file entries have no covering directory in the set; the hook trusts the sentinel and prints the SKIP.

## Proposed Fix

In _record, keep a measured path that fails the existence check instead of dropping it (fall back to the recorded file/dir kind for classification), so staged deletions of suite-read files still count as test-relevant.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
