# BG1165: The TSD's Security Testing section says the script contract forbids network calls except the gh wrapper, but a version-check GET and git fetch origin also call out

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_lean_tsd_refresh.py
> **Evidence:** US1102 builder report, 2026-11-01; tsd.md:386.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T08:07:36Z

## Summary

Found by US1102's builder (2026-11-01). sdlc-studio/tsd.md:386 says 'the script contract forbids network calls except the `gh` wrapper'. The TRD's section 5 Network paths table (US1101) lists three gh callers (`github_sync.gh`, `release_cut.forge_ci_state`, `sprint_report.fetch_ci_runs)` plus `version_check.latest_release`'s HTTPS GET and `sprint.origin_drift`'s `git fetch origin`. The TSD sentence predates run four, and no run-four criterion covers it.

## Steps to Reproduce

1. Read tsd.md:386.
2. Read trd.md's section 5 Network paths table, or grep the shipped scripts for urlopen and a fetch argv.

## Proposed Fix

Point the TSD's sentence at the TRD's network-paths table, naming the version-check GET and the origin fetch as the two non-gh paths.

## Acceptance Criteria

- [ ] **AC1** The TSD's security section names every network path the TRD's table lists, or points at that table, and a test fails if it claims gh is the only one.
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py

## Impact

A security sentence in the TSD understates the network surface.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
