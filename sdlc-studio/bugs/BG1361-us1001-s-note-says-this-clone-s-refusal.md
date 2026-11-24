# BG1361: US1001's note says 'this clone's refusal log', which misleads in a fresh clone

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_yield_frozen.py, changelog.d/BG1361.md
> **Evidence:** RUN-01M77177, 2026-11-12: qa-seat-US1001-r1
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:20:59Z

## Summary

The lane-yield note's wording at HEAD cecc9dfe7 is "The tally is this clone's refusal log as the close read it." (`sprint_report.py` `_lane_yield_section`, frozen branch). The tally was frozen by the closing clone, so in any other clone, where the page is re-derived, 'this clone's' is wrong; the function's own docstring says 'the closing clone's log'. Reproduced by reading the source branch; no test pins the sentence.

## Steps to Reproduce

Read the sentence against the behaviour the review probed.

## Proposed Fix

Reword to what the code does.

## Acceptance Criteria

- [ ] **AC1** Given a run record that froze its lane-yield tally, when the lane-yield section is built from it, then the note names the closing clone's refusal log, not 'this clone's'. Fails on: `_lane_yield_section` appends "This clone's refusal log as the close read it", which in a fresh clone reads as that clone's own log when the tally came from the closing clone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_frozen_tally_names_the_closing_clones_log
  - **Verified:** yes (2026-11-24)

- [ ] **AC2** Given a run record that froze nothing, when the section is built live, then the note adds no closing-clone sentence. Fails on: a reword applied to both branches would claim a closing clone where none froze a tally.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py::LaneYieldTests::test_a_live_tally_names_no_closing_clone
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced the wording at HEAD, ACs split frozen and live branches |
| 2026-11-24 | orchestrator | Affects gains tests/test_lane_yield_frozen.py, whose line 150 pins the old wording the fix corrects (the RS builder's full-suite run) |
