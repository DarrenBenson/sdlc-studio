# BG0324: github_sync cascade conflates a gh failure with 'no merged PRs' and exits 0

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/github_sync.py, .claude/skills/sdlc-studio/scripts/tests/test_github_sync.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

When gh pr list fails (auth, network, timeout), `gh_pr_list_merged` prints one stderr line and returns [], and `cmd_cascade` prints 'no merged PRs found in range' and returns 0 - a successfully-completed-looking cascade that examined zero PRs, the exact failure/empty conflation `gh_issue_list` refuses by name one function earlier.

## Steps to Reproduce

Evidence (`gh_pr_list_merged` lines 156-160; `cmd_cascade` lines 618-620): Lines 158-160 return [] on non-zero returncode; lines 618-620 treat empty as success; `gh_issue_list`'s docstring and GhError:77 document the deliberate distinction; `cmd_push`/`cmd_pull` already return 1 on failure (BG0092) - cascade is the one lane still swallowing it.

## Proposed Fix

Make `gh_pr_list_merged` raise GhError on a gh failure like `gh_issue_list`, and have `cmd_cascade` catch it and return non-zero so failure is never reported as an empty range.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
