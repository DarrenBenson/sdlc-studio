# BG1296: `sprint lane land` names a unit's brief and no-brief note by the unit id as typed, so `--units us0101` writes `us0101-qa.none` beside `US0101-qa.txt` and leaves the canonical brief in place

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1296.md
> **Evidence:** BG1290 round-1 verdict (critic-verdicts.md, probe P3) and round-2 verdict (probe P3)
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T18:17:58Z

## Summary

From BG1290's round-1 and round-2 reviews (qa-seat-BG1290-r1, pre-existing, non-blocking). The brief path is keyed by the raw unit string, not by `sdlc_md.norm_id`: `lane land --units us0101` (the case of a `lane-us0101` worktree) with no self-check removes `us0101-qa.txt` and writes `us0101-qa.none` (lanes.py:220-224, lanes.py:252-254, lanes.py:276), but leaves `US0101-qa.txt` from the earlier round. Under `block` the stale self-check is now refused at `lane accept --unit US0101` (probe P3, round 2). Under `report` that accept still records the verdict, with a warning, against the earlier round's brief. BG1290's fragment now states the keying ("named by the unit id as the command line spells it"), so the text is true; the behaviour is the finding.

## Steps to Reproduce

Land US0101 once with its self-check (writing `US0101-qa.txt`), then run `sprint lane land --units us0101` for a repair with no self-check under `review.author_self_check: report`, then `sprint lane accept --unit US0101` with an APPROVE: it records against round one's brief.

## Proposed Fix

Normalise the unit id with `sdlc_md.norm_id` before naming `briefs/<unit>-qa.txt` and `<unit>-qa.none`, in both `lane land` and `_brief_of`, and pin it with a lower-case landing test.

## Acceptance Criteria

- [ ] **AC1** Given `US0101-qa.txt` left by an earlier landing, when `sprint lane land --units us0101` lands a repair with no self-check, then `US0101-qa.txt` is removed, the note is written as `US0101-qa.none`, and no file named for the lower-case spelling exists under the briefs directory. Fails on: `us0101-qa.none` written beside the earlier round's `US0101-qa.txt`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_lower_case_unit_id_names_the_canonical_brief_and_note
- [ ] **AC2** Given that landing, under `review.author_self_check: report`, when `sprint lane accept --unit US0101` is given an APPROVE, then it is refused for want of a brief and nothing is recorded, and `--unit us0101` is refused the same way. Fails on: the verdict recorded against the earlier round's brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_accept_reads_the_brief_by_the_normalised_unit_id

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
