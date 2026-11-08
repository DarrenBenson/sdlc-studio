# BG1290: `sprint lane accept` records a verdict against the previous round's QA brief when a repair's landing wrote none, so an unchecked repair moves to Done

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1290.md
> **Evidence:** BG1289 review round 1 (qa-seat-BG1289-r1), the [pre-existing] finding; reproduced at 5733b936
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:55:17Z

## Summary

A landing that writes no brief (its self-check was refused or not recorded) leaves the earlier round's `sdlc-studio/.local/briefs/<unit>-qa.txt` in place, and `sprint lane accept` (`_brief_of`, `lib/lanes.py:290`) fingerprints that stale file, records the verdict against it and moves the unit to Done. Under `review.author_self_check: block` the end-to-end gate is therefore bypassed even after BG1289: the landing exits 1 with 'self-check NOT RECORDED', but `lane accept` still closes the unchecked repair. Found by BG1289's independent review (qa-seat-BG1289-r1, round 1), reproduced at 5733b936 and pre-existing at v6.2.0.

## Steps to Reproduce

1. Land a unit with a hand-in, so `lane land` writes `briefs/<unit>-qa.txt`; record a REJECT with `lane accept`. 2. Land a repair whose self-check record is refused (malformed claims): the landing prints 'self-check REFUSED and no brief written'. 3. Run `lane accept --unit <unit> --verdict <APPROVE file>`: it exits 0, records round 2 against round one's brief and moves the unit to Done.

## Proposed Fix

Have `lane land` remove `briefs/<unit>-qa.txt` before it lands, so only a brief written by this landing survives it, and have `_brief_of` refuse a brief whose recorded self-check is not the unit's current one (its Affects digest and commit), naming the landing that wrote no brief.

## Acceptance Criteria

- **AC1:** Given a unit whose round-1 landing wrote `briefs/<unit>-qa.txt` and whose repair landing's self-check was refused or not recorded, when `sprint lane accept` is run with an APPROVE verdict, then it exits non-zero, records nothing and leaves the unit's status unchanged, naming the landing that wrote no brief. Fails on: `_brief_of` fingerprinting round one's file (the reproduced 'APPROVE recorded, round 2 ... moved to Done').
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_accept_refuses_when_the_latest_landing_wrote_no_brief
- **AC2:** Given any `sprint lane land` of a unit, then a QA brief for that unit exists afterwards only if this landing wrote it: a landing that writes none leaves no `briefs/<unit>-qa.txt` behind. Fails on: a landing that leaves the earlier round's brief in place.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_landing_leaves_only_its_own_brief
- **AC3:** Given a repair whose self-check is recorded and whose landing writes a fresh brief, then `lane accept` records the verdict against that fresh brief, as before. Fails on: a fix that refuses every round-2 accept.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_repair_with_its_own_brief_is_accepted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-08 | Claude Opus 5.5 (grooming) | Criteria with Verify lines; joins the 6.3.0 release-blocking set (D0429) |
