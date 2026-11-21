# BG1243: US1124's cost anatomy leaves four rules unpinned: the per-component maximum, the CLI harness fallback and two role assignments

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, changelog.d/BG1243.md
> **Evidence:** run seven (RUN-01M6RAP7) US1124 review rounds 1 and 2
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:06Z

## Summary

Run seven, US1124 rounds 1 and 2 (round 2 APPROVE; the round-1 blocking finding is closed). Cover only, since the shipped behaviour is correct by execution: (1) the repair's per-component maximum in `_largest` (`lib/cost_anatomy.py:116`) is unpinned: the mutant taking the whole copy with the larger output survives all four tests, because the pin's two shared copies differ only in output (`tests/test_cost_anatomy.py:40-41,193`); on a split-component fixture the shipped code reads 16,389, equal to the meter, and the mutant 9,389. (2) The CLI fallback that makes AC4's harness reading reachable is unpinned: AC4's Verify calls `from_reading` directly and mutant `if True:` on the fallback condition (`sprint.py:9057`) survives. (3) The builder as the agent the unit's first verdict names as author when it was not the first returned (mutant `builder = agents[0]`, `lib/cost_anatomy.py:81`) and a reviewer overriding a lane-returned agent (mutant `roles.setdefault(key, REVIEWER)`, :87) both survive.

## Steps to Reproduce

Apply each mutant above in a scratch copy and run `pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py`: every one passes.

## Proposed Fix

Add a fixture whose shared message splits its components the other way (main larger `cache_read`, agent larger output) and assert the anatomy equals the meter; drive `sprint.py cost --anatomy` with `SDLC_STUDIO_HARNESS=copilot` over a `COPILOT_HOME` fixture holding no Claude transcript; add the out-of-order builder and the reviewer-override role cases.

## Acceptance Criteria

- [ ] **AC1** Given a shared message whose main copy holds the larger `cache_read` and whose agent copy holds the larger output, when the anatomy is built, then its total equals the meter's reading of the same transcripts. Fails on: taking the whole copy with the larger output in place of the per-component maximum.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_a_shared_message_split_across_components_equals_the_meter
- [ ] **AC2** Given `SDLC_STUDIO_HARNESS=copilot` and a `COPILOT_HOME` fixture holding no Claude transcript, when `sprint.py cost --anatomy` runs, then it prints the harness reading. Fails on: the fallback condition forced always true or always false going unnoticed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_cli_falls_back_to_the_harness_reading
- [ ] **AC3** Given a unit whose first verdict names as author an agent that was not the first returned, and a reviewer a lane also returned, when the roles are assigned, then the named author is the builder and the reviewer reads as reviewer. Fails on: the first returned agent taken as builder, or a lane-returned role kept over the reviewer's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py::CostAnatomyTests::test_the_builder_is_the_named_author_and_a_reviewer_overrides_a_lane_return

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Cost anatomy is correct by execution; four rules lack tests, and no user-visible claim is false. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
