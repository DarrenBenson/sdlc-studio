# BG1750: BG1251 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1251.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T05:16:04Z

## Summary

BG1251 was rejected at round 2, the review cap, by agent-ae6aa6dce0ac8e256 (engineering), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] a markdownlint that runs past its timeout crashes `sprint lane land` with a Python traceback instead of a refusal: `_refuse_markdown` calls `subprocess.run([lint, "--config", ...], timeout=GIT_TIMEOUT)` (lib/lanes.py:1235-1237) with no handler, and `land` catches only `LandError`. By execution, `_refuse_markdown` over a staged page with a stand-in linter that sleeps past a 2-second `GIT_TIMEOUT` raises `TimeoutExpired` uncaught, and `sprint.main` has no general handler above it. The module's own rule, "A run past `timeout` is a LandError" (lib/lanes.py:1331), is kept by every other subprocess call in the landing, which also runs through `_bounded` to stop the child's process group. `subprocess.run` kills only the direct child, so the linter's own children outlive the timeout. Nothing is committed when it fires, because the lint runs before any step moves. The call is the unit's own, added in c1aa3b055 (`git log -S_refuse_markdown`). The repair is to run it through `_bounded`, or catch `TimeoutExpired` and raise a `LandError` naming the linter and the timeout, with a pin. No open bug covers it; RULINGS: Judged across both rounds (c1aa3b055 and 0bcd03956) in a detached worktree at 0bcd03956. Claim inventory: changelog "names sibling lanes still in flight on one line" TRUE (AC1 test green)\\\; "runs markdownlint over the staged markdown and refuses before the commit when it fails" TRUE for a failing lint (`_refuse_markdown` is called right after `_preflight`, before any step)\\\; "Each page is linted under the config nearest above it, or, in a dot-directory such as `.claude/`, under the one config that directory tracks, as the commit hook does" TRUE against this repository's pre-commit markdown lanes (`.claude/` pages under the skill's config, every other tracked page, `.github/` included, under the root one)\\\; the hand-in line's test-file rule matches what `critic.py self-check record` enforces (`_self_check_scope` reads the same `file_finding.is_test_path` over Affects)\\\; an absent linter is said, pinned at test\_lane\_land.py:299. verify\_ac BG1251 passes 3/3, and test\_lane\_land.py, test\_lean\_lane\_rebrief\_terminal.py, test\_sprint.py::LaneInFlightTests and test\_lane\_builder\_brief.py pass (100 passed). My mutants, each applied once: only the first config group linted (killed by the dot-directory test), the staged list read from the working tree instead of the index (killed by the AC2 test), and the executable check on a `node_modules` linter weakened to `exists()` (killed by the linter-order test). The author's nine mutants replay killed. The `_brief_of` and `_accept` changes in lib/lanes.py within this range belong to commits not naming BG1251 and are not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1251 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1251 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] a markdownlint that runs past its timeout crashes `sprint lane land` with a Python traceback instead of a refusal: `_refuse_markdown` calls `subprocess.run([lint, "--config", ...], timeout=GIT_TIMEOUT)` (lib/lanes.py:1235-1237) with no handler, and `land` catches only `LandError`. By execution, `_refuse_markdown` over a staged page with a stand-in linter that sleeps past a 2-second `GIT_TIMEOUT` raises `TimeoutExpired` uncaught, and `sprint.main` has no general handler above it. The module's own rule, "A run past `timeout` is a LandError" (lib/lanes.py:1331), is kept by every other subprocess call in the landing, which also runs through `_bounded` to stop the child's process group. `subprocess.run` kills only the direct child, so the linter's own children outlive the timeout. Nothing is committed when it fires, because the lint runs before any step moves. The call is the unit's own, added in c1aa3b055 (`git log -S_refuse_markdown`). The repair is to run it through `_bounded`, or catch `TimeoutExpired` and raise a `LandError` naming the linter and the timeout, with a pin. No open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1251 AC1 still passes: Given two lanes in flight, when `sprint.py lane brief` briefs a third unit, then one line names the units in flight, and the full restart warning is printed only for the briefed unit when it is itself in flight. Fails on: one WARNING per sibling lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightTests::test_a_brief_names_sibling_lanes_in_one_line
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** BG1251 AC2 still passes: Given a hand-in whose changelog fragment has a wrapped line opening `+ 3`, when `sprint.py lane land` runs, then it refuses before the commit, naming the file and the markdown rule, and a clean hand-in beside it lands. Fails on: the refusal arriving from the commit hook, or an absent linter read as a pass without saying so.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_hand_in_fragment_that_fails_markdownlint_is_refused_before_the_commit
  - **Verified:** yes (2026-11-25)
- [ ] **AC4** BG1251 AC3 still passes: Given a unit whose Affects declares test files, when its lane brief is printed, then the hand-in line names the accepted rulings TRUE, FALSE and UNVERIFIABLE, written bare, and says each mutant's test is a `path::name` in one of those test files, naming them. Fails on: a line naming only the field names.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_hand_in_line_names_the_accepted_rulings_and_test_files
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
