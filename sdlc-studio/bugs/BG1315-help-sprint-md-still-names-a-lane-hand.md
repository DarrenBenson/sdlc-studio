# BG1315: `help/sprint.md` still names a lane hand-in `<unit>-claims.json` under the id as typed, which BG1303's landing now keys by the normalised id, and `refine seams` still pairs a schema-3 unit with itself

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
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

- [ ] **AC1** The behaviour described is corrected: From the QA reviews of BG1302 and BG1303 (qa-seat-BG1302-r1, qa-seat-BG1303-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Say in help/sprint.md that the hand-in names use the normalised id (`lanes.hand_in_names`), and dedupe by `sdlc_md.norm_id` in `refine.seam_map` as...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
