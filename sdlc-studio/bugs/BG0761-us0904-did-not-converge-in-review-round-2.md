# BG0761: US0904 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Depends on:** BG0759 - its carried patch applies only over the rebased pre-commit hook (QA grooming)
> **Carried work:** the round-2 patch is kept at sdlc-studio/.local/US0904-carried-r2.patch, complete against 25cbd375 and passing every other probe. Remaining fix: in sprint_report.classify_refusals change `when > at` to `when >= at` (git stamps a commit when it starts, before its hooks) and add a fixture row whose retry carries the refusal's own second; then add the message-refusal test to AC1's Verify line and reword AC2 to the blob rule
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-commit, .githooks/commit-msg, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, tools/tests/test_lean_refusal_log.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, changelog.d/US0904.md, sdlc-studio/stories/US0904-each-lane-s-refusals-are-counted-against-the.md
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0904 was rejected at round 2, the review cap, by qa-rev-US0904, so it was carried as a known issue rather than reviewed again. The findings still open: [new] classify\_refusals joins by committer time strictly after the refusal, but git stamps a commit when it starts, so a same-second retry reads pending: fix is when >= at plus a same-second fixture row [LC-002]; [new] non-blocking: git log --raw without -z quotes non-ASCII paths so they misclassify; [new] non-blocking: commit-msg blob recording unpinned [LC-002]; [new] non-blocking: AC2 text still says any code change is a catch while the pinned rule is blob-based; [new] non-blocking: AC1 Verify line omits the message-refusal test [LC-002]; [new] non-blocking: a missing log means both no-refusal-yet and consuming project [LC-006]

The criteria below take the blocking finding and the two the carried-work note names; the other non-blocking findings are not re-opened. Known limit, not in scope: refusal stamps and committer times are both whole seconds, so under `>=` a commit that landed in the refusal's second but BEFORE it would be read as its retry. The lean shape gives each criterion one Verify line, so the message-refusal test becomes its own criterion rather than a second selector on US0904 AC1.

## Steps to Reproduce

At 65cdf1ca the patch applies cleanly (`git apply --check`) and its seven tests pass on HEAD plus the patch. In a git fixture whose retry commit is stamped 10:00:05, `classify_refusals` with the patch applied answers `pending` for a refusal stamped 10:00:05 and `catch` for one stamped 10:00:04. HEAD has no `classify_refusals`: US0904 is undelivered.

## Proposed Fix

Apply the carried patch, change `when > at` to `when >= at`, add the same-second fixture row, add US0904 AC5 for the message refusal, and reword US0904 AC2 to the blob rule.

## Acceptance Criteria

- [ ] **AC1** Given the carried patch applied and a refusal stamped in the same second as the commit that followed it, when `sprint close` classes the refusal, then it is classed `catch` or `paperwork` by that commit, never `pending`. Fails on: the carried patch's `when > at`, which answers `pending`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_retry_in_the_refusals_own_second_is_classed_by_that_retry
- [ ] **AC2** Given a logged refusal and the next commit, when it is classed, then it is a candidate catch only when that commit writes a non-paperwork path to a blob other than the one the refused commit staged, and a retry carrying the refused blob unchanged is paperwork; US0904 AC2's text states this blob rule. Fails on: the rule US0904 AC2 still words, "any code or test change is a catch", under which a retry of the unchanged refused code counts as a catch.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_refusal_is_classed_by_the_commit_that_followed_it
- [ ] **AC3** Given a commit refused by the commit-msg hook's message rules, when the hook exits, then one line naming the message lane and the staged blobs is appended to `sdlc-studio/.local/refusals.jsonl` and no repo-writes snapshot is left open; this is US0904 AC5. Fails on: dropping the commit-msg hook's logging call, or logging before the snapshot is released.
  - **Verify:** pytest tools/tests/test_lean_refusal_log.py::RefusalLogTests::test_a_refused_message_is_logged_and_leaves_no_snapshot_open

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (patch applies cleanly at 65cdf1ca, its 7 tests pass, and a same-second retry reads `pending` when run); criteria are the carried patch plus its remaining fix, each with one Verify line and the wrong fix it fails on; Affects set to the patch's files plus US0904; 3 points resized to 2 |
