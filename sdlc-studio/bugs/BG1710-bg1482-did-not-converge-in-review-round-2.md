# BG1710: BG1482 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG1482.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/reference-retro.md
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T17:18:47Z

## Summary

BG1482 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's AC1 test docstring misstates its own mutant. It says "MUTANT: cap the build digest at INJECT\_MAX + 1 - six pass, and of eleven the five oldest zero-hit traps fall out" (tests/test\_lessons.py:2010-2011). The fixture gives every class above LC-003 one hit (`_hit`, tests/test\_lessons.py:2002-2003), so only LC-001 to LC-003 are zero-hit. By execution, over that eleven-class store `active_for` ranks LC-011 to LC-004 first and a cap of six drops LC-005 (1 hit), LC-004 (1 hit), LC-003, LC-002 and LC-001. The five oldest fall out, and two of them are not zero-hit traps. Reword it, for example "the five oldest fall out, the three zero-hit traps among them"; RULINGS: Prior finding "The claim that a lane brief has no cap is pinned only at six classes" is CLOSED. The AC1 test now builds 2 x INJECT\_MAX + 1 live build classes and asserts every id in the digest, every rule in the rendered block, "Lessons for build (11 of 11 active)" and no "more active" line. `rows[:INJECT_MAX + 1]` is killed (my replay: 1 failed, 144 passed over test\_lessons.py). So is `rows[:2 * INJECT_MAX]` (1 failed, 3 passed over QuietBuildClassTests). Any finite fixture admits a cap one larger, and 2 x INJECT\_MAX + 1 is the bound round one asked for. Round one's pre-existing finding on the `active_for` docstring is CLOSED inside the unit. lessons.py:2021-2022 now says `phase_digest` caps plan and review, never build, and the renderer says how many it dropped. Both are TRUE: phase\_digest (lessons.py:2039) caps every phase but build, PHASES is plan, build and review, and render\_phase prints the "+N more active" line. verify\_ac run --id BG1482 --dry-run reports 2 of 2 criteria passing. Claim inventory for the repair: the changelog's new sentence on the `active_for` docstring is TRUE. The rest of changelog.d/BG1482.md was ruled TRUE in round one and is unchanged in substance. tools/lint-style.sh passes. The author's 4 recorded mutants all replay killed. My own pass: 2 mutants, both killed (a build cap of INJECT\_MAX + 1, and of 2 x INJECT\_MAX). The finding is a claim-inventory FALSE, settled by running `active_for` over the eleven-class store. The lessons.py `recorded_with_no_run` hunk and the RunRepeatHitTests hunks in this commit belong to BG1436 and BG1483 and were not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1482 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1482 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's AC1 test docstring misstates its own mutant. It says "MUTANT: cap the build digest at INJECT\_MAX + 1 - six pass, and of eleven the five oldest zero-hit traps fall out" (tests/test\_lessons.py:2010-2011). The fixture gives every class above LC-003 one hit (`_hit`, tests/test\_lessons.py:2002-2003), so only LC-001 to LC-003 are zero-hit. By execution, over that eleven-class store `active_for` ranks LC-011 to LC-004 first and a cap of six drops LC-005 (1 hit), LC-004 (1 hit), LC-003, LC-002 and LC-001. The five oldest fall out, and two of them are not zero-hit traps. Reword it, for example "the five oldest fall out, the three zero-hit traps among them"
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1482 AC1 still passes: Given a lessons store holding six live build-injected classes, the oldest three with zero hits, when the lane brief's lessons block is built, then no live build class is missing from it: either all six are carried, or the sixth was refused at class-add with a message to graduate one first. Fails on: the `INJECT_MAX` cap dropping the oldest zero-hit builder trap from the lane brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::QuietBuildClassTests::test_no_live_build_class_falls_out_of_the_lane_brief
- [ ] **AC3** BG1482 AC2 still passes: Given more than `INJECT_MAX` live classes injected at plan, when the plan digest is built, then it still carries `INJECT_MAX` of them and says how many it dropped. Fails on: the cap lifted for every phase, not only for build.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::QuietBuildClassTests::test_a_phase_other_than_build_is_still_capped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | BG1482 approved in its ruled round three (D0585); the round-two findings closed by that review, its own criteria pass |
