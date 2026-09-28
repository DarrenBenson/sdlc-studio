# BG0819: A signed sprint report's 'Verified on' names the run's base ref, the commit before any work, because nothing writes verified_sha

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_verified_on.py, changelog.d/BG0819.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** eval 09 run v6-main: /tmp/evals-v6-main/09-lean-sprint RPT0001 line 10 vs `git log` (eac8efe is `fixture base`); sdlc-studio/reports/RPT0010 line 10 names 1c404a48 (the plan commit); grep -rn verified_sha scripts/ finds only the reader (sprint_report.py:3715)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:24:00Z

## Summary

`sprint_report.py` fills the page's `Verified on:` from `state.get('verified_sha') or state.get('base_ref')`, and no code writes `verified_sha`, so every report states the commit the run was PLANNED from as the commit it was verified on. Eval 09 (v6-main) signed RPT0001 `Verified on: eac8efe` = `fixture base`, three commits before the close. This repository's RPT0010 reads `Verified on: 1c404a48`, the plan commit. The fingerprint the operator signs covers a page that misstates where its evidence came from.

## Steps to Reproduce

Run any sprint to close; read the report's `Verified on:`; `git log --oneline -1 <sha>` names the commit the run started from.

## Proposed Fix

Stamp `verified_sha` on the run state at PREPARE, as `record_close_tree` stamps the tree, from the HEAD the close ran its gate against; with none recorded print `not recorded`, never the base ref.

## Acceptance Criteria

- [ ] **AC1** Given a run closed at a commit after its base ref, when the report is drawn, then `Verified on:` names the commit the close's gate ran against. Fails on: HEAD, which prints the base ref
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_verified_on.py::ReportVerifiedOnTests::test_the_close_commit_is_named
- [ ] **AC2** Given a run state with no verified commit recorded, then `Verified on:` reads `not recorded`. Fails on: falling back to the base ref
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_verified_on.py::ReportVerifiedOnTests::test_no_record_is_not_the_base_ref

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
