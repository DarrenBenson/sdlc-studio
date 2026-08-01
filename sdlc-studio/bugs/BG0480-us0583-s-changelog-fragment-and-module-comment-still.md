# BG0480: US0583's changelog fragment and module comment still describe the narrow scan that _standing_prose replaced

> **Status:** Fixed
> **Verification depth:** functional (both prose sites corrected against the shipped behaviour of _standing_prose)
> **Severity:** High
> **Points:** 2
> **Affects:** changelog.d/US0583.md, tools/check_spec_claims.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** independent-critic (qa seat); human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

changelog.d/US0583.md states "The scan is deliberately narrow: only lines the diff ADDS, only within that diff", and the module comment in tools/`check_spec_claims.py` echoes it. `_standing_prose`, added later in the same sprint, reads all 181 changelog.d/*.md fragments regardless of the diff, so neither claim is true of the shipped code.

Evidence: on commit 6f91b24b the lane sourced findings from changelog.d/BG0348.md, which that commit does not touch - `git show 6f91b24b --stat | grep -c BG0348` returns 0. And `git show dffea4bf --stat | grep -c US0583` returns 0, so the fragment was never reopened when the behaviour moved past it.

This is BG0471's exact shape: prose left asserting the old behaviour after a later commit moved the code. It shipped inside the batch built to detect that shape.

## Steps to Reproduce

1. git show 6f91b24b --stat | grep -c BG0348 -> 0, yet the lane cites BG0348.md on that commit.
2. git show dffea4bf --stat | grep -c US0583 -> 0: the fragment was not updated when `_standing_prose` landed.
3. Read changelog.d/US0583.md against the body of `_standing_prose.`

## Proposed Fix

Correct the fragment and the module comment to describe what the scan reads: added lines within the diff for one channel, and the whole standing changelog.d corpus for the drift channel. State the second explicitly, because it is the surprising half and the one whose cost and noise the reader needs to know about.

## Acceptance Criteria

- [ ] The behaviour described is corrected: changelog.d/US0583.md states "The scan is deliberately narrow: only lines the diff ADDS, only within that diff", and the module comment in...
- [ ] The proposed fix lands, pinned by a test: Correct the fragment and the module comment to describe what the scan reads: added lines within the diff for one channel, and the whole standing changelog.d...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | independent-critic (qa seat) | Filed |
