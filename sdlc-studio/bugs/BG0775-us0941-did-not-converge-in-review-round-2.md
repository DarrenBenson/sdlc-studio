# BG0775: US0941 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py, changelog.d/US0941.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_findings_window.py, changelog.d/BG0775.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T17:31:14Z

## Summary

US0941 was rejected at round 2, the review cap, by qa-rev-US0941, so it was carried as a known issue rather than reviewed again. The findings still open: [regression] a merged side branch defeats the anchor without rewriting history because \_signed\_page reads plain git log on the path and history simplification drops the real signing commit, so hide-an-open-High and inflate-points forgeries read VALID, fix with --full-history and disagreeing signed versions read INVALID, about 10 lines plus a merge test; [regression] a forged page minted under a new report id certifies itself, fix by anchoring only the page the run record's signature names, about 8 lines plus a test; [new] non-blocking: the earliest-signed-version rule is untested, a latest-version mutant survives [LC-002]; [new] non-blocking: the anchor lookup passes str(path) as a pathspec so a relative-root library caller falls back to the tree

## Steps to Reproduce

1. Read the round 2 REJECT of US0941 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0941 again in a later run.

## Acceptance Criteria

- [ ] **AC1** Given US0941's carried work (sdlc-studio/.local/US0941-carried-r2.patch) applied onto main, then US0941's five criteria pass through their Verify selectors and RPT0006-RPT0009 check VALID. Fails on: a landing that drops the signed-page anchor or the page's own readings
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py
- [ ] **AC2** Given a signed report whose page is forged on a side branch (hide an open High, inflate a unit's points, fingerprint recomputed) and merged back with `-X theirs`, when `sprint_report.py check` runs, then it reads INVALID naming the commits whose signed versions disagree. Fails on: reading the path's history without `--full-history`, where simplification drops the real signing commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_page_forged_on_a_merged_branch_is_invalid
- [ ] **AC3** Given a copy of a signed page committed under a new report id with a figure forged and the principal kept, when `check` runs on the new id and `status.py` reports it, then it is not VALID and not reported as signed, because only the page the run record's signature names is anchored. Fails on: taking any principal-bearing page's first commit as its own anchor
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_page_minted_under_a_new_id_does_not_certify_itself
- [ ] **AC4** Given a forged signed version committed on top of the real signed page, then `check` reads it INVALID against the EARLIEST signed version. Fails on: taking the latest signed version as the anchor
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_later_signed_version_does_not_replace_the_anchor

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Engineering seat | Groomed: lands US0941's carried work with the two anchor bypasses closed (merged side branch, a page minted under a new id) and the earliest-version rule pinned; US0941 is never-cut under D0275 |
