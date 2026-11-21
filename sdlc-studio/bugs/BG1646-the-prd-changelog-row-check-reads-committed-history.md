# BG1646: The PRD changelog-row check reads committed history, so a commit that changes the PRD without a row passes its own hooks

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_prd_refresh.py, .githooks/commit-msg
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T01:43:42Z

## Summary

BG1168 (fixed in 6d3cd7e6, RUN-01M7TTK3) added `PrdRulesTests.test_every_prd_change_since_6_1_0_has_a_changelog_row`, which walks git log for commits that touched sdlc-studio/prd.md and refuses one whose subject names no unit in the PRD's Changelog table. A commit cannot appear in its own history while its pre-commit hook runs, so the commit that breaks the rule passes every hook and the first thing to refuse it is the push gate, after more commits are stacked on it. 6aee7a42 (US1299) changed the PRD with no row, passed lane land's hooks, and main stayed unpushable until a repair added the row.

## Steps to Reproduce

Stage a change to sdlc-studio/prd.md with a commit subject naming a unit the Changelog table does not name, and commit: the hooks pass. Then run pytest tools/tests/`test_lean_prd_refresh.py` -k `changelog_row`: it fails on that commit.

## Proposed Fix

Judge the staged change at commit time: in the commit-msg hook, or a pre-commit lane that reads the staged prd.md and the message, refuse a PRD change whose subject's units are named by no Changelog row; keep the history test as the push-time backstop.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1168 (fixed in 6d3cd7e6, RUN-01M7TTK3) added `PrdRulesTests.test_every_prd_change_since_6_1_0_has_a_changelog_row`, which walks git log for commits that...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Stage a change to sdlc-studio/prd.md with a commit subject naming a unit the Changelog table does not name, and commit: the hooks pass.
- [ ] **AC3** The proposed fix lands, pinned by a test: Judge the staged change at commit time: in the commit-msg hook, or a pre-commit lane that reads the staged prd.md and the message, refuse a PRD change whose...

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it affects only this repository's own CI, hooks or tools, nothing a consuming project installs. The PRD changelog-row check runs in the push gate's history walk, not the commit hooks; a missing row is caught later in this repository. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
