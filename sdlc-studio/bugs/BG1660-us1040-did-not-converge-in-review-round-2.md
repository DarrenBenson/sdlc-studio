# BG1660: US1040 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/lib/persona_goals.py, changelog.d/BG1660.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T09:02:31Z

## Summary

US1040 was rejected at round 2, the review cap, by agent-a66af32d347274788 (engineering), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] `goal_trace` joins each traced End goal to its Verify by the number on the card (sprint.py:11844-11845, `goal_verify.get(n)` over the number-keyed dict sprint.py:11781 builds, which a011a415 added and nothing read until this diff, `git log -S` naming 96f53a41 alone for the join), so a card whose End goals repeat a number gives every one of them the last Verify. Markdown's lazy numbering, every item `1.`, is such a card, and this repo's markdownlint config keeps MD029's default, which accepts it. Probed through `sprint.py plan --format json` and `goal-review brief` in a fixture: End goal 1 carrying a pytest Verify and the next carrying `manual walk each room`, numbered `1.` and `2.`, reads `checkable` true (the positive control)\; the same card numbered `1.` and `1.` reads `checkable` false, lists both goals as checked by hand, and the plan and the brief both print `goal check: NONE - nothing can check this goal`, false advice about a goal an executable Verify checks, against AC3's reading of an End goal that gains one. With the second goal carrying no Verify, the brief lists it with goal 1's Verify and `checked_by` names it as an executable check. No fixture can see it: `_card` numbers goals with `enumerate`, so a number-keyed and a position-keyed join agree by construction, and my mutant R3, joining on list position, survived all 5 tests. Carry each End goal's own Verify with it (`persona_goals.end_goals` already pairs them) rather than re-joining on the number, and add a fixture that repeats a number; [new] the backtick strip in `_end_goal_check` (sprint.py:11860) is unpinned: an empty code-span Verify, two backticks and nothing between, reads `none` at HEAD, and the mutant that drops the strip reads it `executable` and survives all 5 tests (R1, re-tested in isolation), because the empty-Verify fixture carries no backticks and the placeholder fixture is caught by the placeholder test whatever the strip does; [new] the role label in the brief's `Traced End goals` listing (sprint.py:13026) is unpinned: every fixture whose traced block is asserted traces a Primary persona, so the mutant that labels every traced persona Primary survives all 5 tests (R2). AC2's Secondary persona, Hana Ito, is asserted only on the goal-check line; [pre-existing] BG1650 a nested Verify attaches to the last numbered goal and a goal's second Verify replaces its first, in `persona_goals.end_goals`, which the new listing reads\; recorded there, not this diff's; RULINGS: Judged 96f53a41 alone: the brief's diff against 958701b5 also carries US1036's `--seat` framing and a011a415's `sprint_serves`, `_live_run` and `persona_cards` hunks, which are not this unit's. Claim inventory: the commit message's claims TRUE\\\; the docstrings of `goal_trace`, `_end_goal_check`, `_end_goal_label` and `_goal_check_line` and the two new comments TRUE, `executable` meaning what `verify_ac` would run rather than count as manual or unspecified\\\; changelog.d/US1040.md TRUE except that `checked_by` names each executable End goal, FALSE on a card that repeats a number (the blocking finding, not a separate one)\\\; help/sprint.md TRUE, though its row reads as if the brief lists the End goals only when the goal is uncheckable, where it lists them whenever the goal traces to a persona\\\; reference-sprint.md TRUE, its plan printing `goal_trace.checkable` meaning the JSON plan. Exercised: `verify_ac.py run --id US1040 --dry-run` 4 of 4 pass\\\; the 5 tests pass in about 66 s\\\; probes through the plan and the brief confirmed a backticked manual Verify reads checked by hand, a traced card with no End goals prints the goal-check line, a Negative persona named beside Maya is not traced, and `--serves maya` traces Maya and flags the goal. Mutation pass, 6 mutants through `mutation.py run`: R4 (a manual End goal counted in `checkable`), TM1 (AC2's fixture given an executable End goal) and TM2 (AC3's goal traced to Hana too) killed\\\; R1, R2 and R3 survived, each re-tested in isolation. The module's 66 s, mostly plan runs, is a note for the suite budget, not a finding.

## Steps to Reproduce

1. Read the round 2 REJECT of US1040 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US1040 again in a later run.

## Acceptance Criteria

- [ ] **AC1** Given a traced persona whose End goals are numbered `1.` `1.` `1.` (Markdown's repeated-number list style) with goal one carrying no Verify, goal two an executable Verify and goal three `Verify: manual walk each room`, when `sprint.py goal-review brief` and `plan --format json` run, then each goal is listed with its own check exactly as for the same card numbered `1.` `2.` `3.`, and `goal_trace.checkable` is true
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::RepeatedNumberTests::test_goals_numbered_alike_keep_their_own_checks
- [ ] **AC2** Given an End goal whose Verify is an empty code span (two backticks), when the brief lists it, then it reads as carrying no check, as a goal with no Verify does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::RepeatedNumberTests::test_an_empty_code_span_verify_is_no_check
- [ ] **AC3** Given two traced personas of different Cast roles, when the brief prints its Traced End goals listing, then each persona's block names that persona's role
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::RepeatedNumberTests::test_the_traced_listing_names_each_personas_role
- [ ] **AC4** US1040 AC1 still passes: Given a traced persona whose End goal 1 carries no Verify, End goal 2 an executable Verify and End goal 3 `Verify: manual walk each room`, when `sprint.py goal-review brief --goal` runs on a goal naming that persona, then End goal 2 is listed with its Verify, End goal 3 as checked by hand and End goal 1 as not testable, each under its number as on the card.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::TestableListingTests::test_brief_lists_each_end_goal_with_its_check
- [ ] **AC5** US1040 AC2 still passes: Given a Sprint Goal that traces to one or more personas none of whose End goals carries an executable Verify, when the goal-review brief and `sprint.py plan --sprint-goal` run, then each prints one goal-check line naming those personas and saying nothing can check the goal, while the plan's exit code and batch are the same as without the line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckTests::test_goal_with_no_executable_end_goal_is_named_on_brief_and_plan
- [ ] **AC6** US1040 AC3 still passes: Given a goal tracing to Maya Okafor, whose End goals carry no Verify, while an untraced persona's End goal carries one, when `sprint.py plan --format json` runs, then `goal_trace.checkable` is false, and once Maya's End goal 1 gains an executable Verify the same plan reports it true and names that goal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckTests::test_checkable_reads_only_the_traced_personas
- [ ] **AC7** US1040 AC4 still passes: Given a goal that traces only to a PRD outcome, and a goal that traces to nothing, in a project whose End goals carry no Verify lines, when the goal-review brief and `sprint.py plan` run, then the outcome-only goal prints no goal-check line, and the untraced goal prints only today's single `Goal serves: NONE` line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_testable_goals.py::GoalCheckBoundaryTests::test_outcome_only_and_untraced_goals_print_no_goal_check

AC1 must fail on: a join keyed by the number written on the card, so repeated numbers hand every goal the last goal's Verify. BG1650 (a nested Verify attaching to the last goal) is a separate, pre-existing Low and is not this bug's to fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
