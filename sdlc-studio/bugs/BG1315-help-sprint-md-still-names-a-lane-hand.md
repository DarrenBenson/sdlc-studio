# BG1315: `help/sprint.md` still names a lane hand-in `<unit>-claims.json` under the id as typed, which BG1303's landing now keys by the normalised id, and `refine seams` still pairs a schema-3 unit with itself

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Evidence:** BG1302-verdict-r1 and BG1303-verdict-r1 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T14:31:10Z

## Summary

From the QA reviews of BG1302 and BG1303 (qa-seat-BG1302-r1, qa-seat-BG1303-r1, non-blocking, 2026-11-09). (1) help/sprint.md:559 and :608 still describe the hand-in as `<unit>-claims.json`, so a builder following the help with a hyphenated schema-3 id writes a file `lane land` no longer reads, and the refusal comes only after the commit. (2) BG1302 put the self-seam guard in `sprint._batch_seams`, so `refine seams --units "US-01M6XQJF US01M6XQJF"` (`refine.seam_map)` still pairs the unit with itself. BG1296 holds the QA brief path keyed by the typed id.

## Steps to Reproduce

1. Read help/sprint.md:559 and :608: they name `<unit>-claims.json` without saying the id is normalised.
2. Run `refine.py seams --units "US-01M6XQJF US01M6XQJF"` in a scratch schema-3 project: it reports a seam between the unit and itself.

## Proposed Fix

Say in help/sprint.md that the hand-in names use the normalised id (`lanes.hand_in_names`), and dedupe by `sdlc_md.norm_id` in `refine.seam_map` as `lane_dispatch` now does; pin both.

## Acceptance Criteria

- [ ] **AC1** Given a schema-3 project, when `refine.py seams --units "US-01M6XQJF US01M6XQJF"` names one unit in two spellings, then no seam is reported and the unit is counted once. Fails on: the unit paired with itself.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamMapTests::test_one_unit_named_in_two_spellings_is_not_a_seam_with_itself
- [ ] **AC2** Given the two passages of `help/sprint.md` that describe a lane's hand-in, when they are read beside `lanes.hand_in_names` for a hyphenated schema-3 id, then each says the file names use the normalised id, and the names the help gives are the ones `lane land` reads. Fails on: the help naming `<unit>-claims.json` under the id as typed, so a builder writes a file the landing does not read.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_help_names_the_hand_in_files_by_the_normalised_id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
