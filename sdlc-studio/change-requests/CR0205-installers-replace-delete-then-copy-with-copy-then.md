# CR-0205: installers: replace delete-then-copy with copy-then-swap so a failed install cannot destroy the previous one

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

install.sh:286-296 (and sweep_stale :346-348) does rm -rf "$dest" then cp -r; install.ps1:240-241,:271-272 the same. Between the delete and a completed copy (disk full, permissions, Ctrl-C), the user's only copy of the skill is gone or half-copied; under set -e the script aborts leaving no install. Re-run heals only once the underlying issue is resolved - the failure erases a previously good install rather than leaving it untouched. Found by RV0007.

## Acceptance Criteria

- [ ] Both installers copy to a sibling temp dir then swap (mv/rename), so an interrupted install leaves the previous copy intact
- [ ] The sweep path uses the same pattern
- [ ] A simulated copy failure (e.g. read-only parent) leaves the prior install untouched and exits non-zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
