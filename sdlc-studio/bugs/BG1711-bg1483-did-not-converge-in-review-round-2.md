# BG1711: BG1483 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG1483.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-retro.md, tools/tests/test_lean_prd_refresh.py
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T17:19:50Z

## Summary

BG1483 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The rule that a code inside an HTML comment in the retro does not count (changelog.d/BG1483.md:8, reference-retro.md:205 "outside an HTML comment") is pinned only for a comment on one line. Dropping `flags=re.S` from the comment strip in `run_citations` (lessons.py:2157), so that a comment spanning lines is no longer removed, SURVIVES RunRepeatHitTests (6 passed). It also SURVIVES test\_lessons.py, test\_lean\_lessons.py, test\_lesson\_no\_run\_retire.py, test\_lessons\_log\_lints.py and test\_persona\_memory\_propose.py (199 passed, 1 skipped). Both comments in the AC2 fixture (tests/test\_lessons.py:2217-2220) sit on one line. Probed alone through `lessons.run_citations`, with a Keep section holding "- the gate held" and then a three-line comment whose middle line reads "Guidance: cite a repeated class as LC-003 here.": HEAD returns no citation, and the mutant returns `('LC-003', 'RETRO9999 Keep')`, a repeat counted from guidance text. Guidance blocks in markdown comments usually span lines. Add a multi-line comment citing a class to the AC2 fixture's Keep or Stop and assert that the class gains no hit; RULINGS: Prior finding "AC1's a bug filed in the run is pinned only for a bug that is still Open" is CLOSED. BG0004, filed in the run and Fixed, gives LC-004 its hit, and `placed = set(_open or ())` is now killed (my replay: 1 failed). Prior finding "The changelog's and reference-retro.md's none when a REJECT or a Try item already hit it this run is pinned only for a REJECT" is CLOSED. LC-002, hit by the retro's tagged Try item, keeps only its `retro:` hit beside BG0002. Guards that skip a Try item's hit are killed, the author's and mine (a guard reading only `critic:` and `cited:` sources: 1 failed, 2 passed). Prior finding "Stripping HTML comments without crossing between them is not pinned" is CLOSED. The second comment, in Try, makes the greedy strip `<!--.*-->` swallow Stop, and it is now killed (1 failed, 5 passed). The comment rule's multi-line half was not raised in round one and is the new finding above. verify\_ac run --id BG1483 --dry-run reports 3 of 3 criteria passing. Claim inventory for the repair, which changes only test\_lessons.py: the three new docstring passages (BG0004 Fixed counts, the Try item's hit is the run's one hit, the second comment follows Stop in Try) and their MUTANT lines are TRUE by execution. changelog.d/BG1483.md and reference-retro.md are unchanged since round one, where they were ruled TRUE. The retro template and this repository's retros use `## Keep` and `## Stop`, which match CITING\_SECTIONS, and no retro here yet holds a comment in either section. The author's 16 recorded mutants all replay killed. My own pass: 5 mutants, 4 killed (the three round-one survivors, and a guard that skips a Try item's hit) and 1 survived, the finding, re-probed alone. The lessons.py hunks in commit 1736835c (the `active_for` docstring and `recorded_with_no_run`) belong to BG1482 and BG1436. The test\_lessons.py QuietBuildClassTests hunk belongs to BG1482. None of these was judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1483 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1483 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The rule that a code inside an HTML comment in the retro does not count (changelog.d/BG1483.md:8, reference-retro.md:205 "outside an HTML comment") is pinned only for a comment on one line. Dropping `flags=re.S` from the comment strip in `run_citations` (lessons.py:2157), so that a comment spanning lines is no longer removed, SURVIVES RunRepeatHitTests (6 passed). It also SURVIVES test\_lessons.py, test\_lean\_lessons.py, test\_lesson\_no\_run\_retire.py, test\_lessons\_log\_lints.py and test\_persona\_memory\_propose.py (199 passed, 1 skipped). Both comments in the AC2 fixture (tests/test\_lessons.py:2217-2220) sit on one line. Probed alone through `lessons.run_citations`, with a Keep section holding "- the gate held" and then a three-line comment whose middle line reads "Guidance: cite a repeated class as LC-003 here.": HEAD returns no citation, and the mutant returns `('LC-003', 'RETRO9999 Keep')`, a repeat counted from guidance text. Guidance blocks in markdown comments usually span lines. Add a multi-line comment citing a class to the AC2 fixture's Keep or Stop and assert that the class gains no hit
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1483 AC1 still passes: Given an open run in which a bug is filed whose summary cites a recorded class by its code, when the run closes, then that class gains one hit for the run, naming the bug. Fails on: a repeat caught by the land or the push gate, and filed as a bug, leaving the class at the hits it had.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_bug_filed_in_the_run_citing_a_class_is_a_hit
- [ ] **AC3** BG1483 AC2 still passes: Given a retro whose Stop or Keep section cites a class code, when the run closes, then the class gains one hit for the run. Fails on: only Try items and cited REJECTs being counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_stop_or_keep_item_citing_a_class_is_a_hit
- [ ] **AC4** BG1483 AC3 still passes: Given one repeat cited by a bug of the run and by the retro, and a bug citing the class that was filed before the run opened, when the run closes and then closes again, then the class holds one repeat for the run and the earlier bug adds none. Fails on: the same repeat counted twice, a re-run close adding a hit, or a bug from outside the run counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::RunRepeatHitTests::test_a_repeat_is_counted_once_and_only_from_this_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | BG1483 approved in its ruled round three (D0586); the round-two findings closed by that review, its own criteria pass |
