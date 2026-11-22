# BG1482: A build-injected lesson class can no longer retire, so once more than INJECT_MAX build classes are live the digest cap drops the oldest builder traps

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, changelog.d/BG1482.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py, .claude/skills/sdlc-studio/reference-retro.md
> **Evidence:** sdlc-studio/reviews/verdicts/BG1474/8dc244746ca5-ede8b0eb.txt, finding 1 and 2.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T21:30:53Z

## Summary

BG1474's QA review (verdict 8dc244746ca5-ede8b0eb) found the build exemption unbounded. A build class with fewer than `GRADUATE_AT` repeats now never leaves, and the lane brief's digest sorts by hits then newest id and slices to `INJECT_MAX` (5) (lessons.py near 2022 and 2034). With more than five live build classes the oldest zero-hit traps, LC-019 to LC-021 among them, fall out of the brief and `test_the_lane_brief_carries_the_builder_traps` goes red as it did for BG1474. Three build classes are live today. Also, `close_pass`'s docstring says a builder trap reaches every brief; a build-only class reaches only the lane brief.

## Steps to Reproduce

1. Add three more build-injected classes to a lessons store holding LC-019 to LC-021 with zero hits.
2. Build the lane brief's lessons block: LC-019 is dropped by the cap.

## Proposed Fix

Never cap a build class out of the lane brief (carry every live build class, as the test demands), or refuse a sixth live build class at class-add with a message to graduate one first; correct the docstring.

## Acceptance Criteria

- [ ] **AC1** Given a lessons store holding six live build-injected classes, the oldest three with zero hits, when the lane brief's lessons block is built, then no live build class is missing from it: either all six are carried, or the sixth was refused at class-add with a message to graduate one first. Fails on: the INJECT_MAX cap dropping the oldest zero-hit builder trap from the lane brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::QuietBuildClassTests::test_no_live_build_class_falls_out_of_the_lane_brief
- [ ] **AC2** Given more than INJECT_MAX live classes injected at plan, when the plan digest is built, then it still carries INJECT_MAX of them and says how many it dropped. Fails on: the cap lifted for every phase, not only for build.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::QuietBuildClassTests::test_a_phase_other_than_build_is_still_capped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-two orchestrator) | Affects widened in-run on lane R's BLOCKED hand-in: the full suite's test_lean_lessons.py pins the five-class build cap that AC1 removes, and reference-retro.md says a brief carries 'at most five' lessons |
