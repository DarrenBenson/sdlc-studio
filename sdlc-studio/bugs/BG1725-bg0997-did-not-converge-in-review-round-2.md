# BG1725: BG0997 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, changelog.d/BG0997.md
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T09:44:29Z

## Summary

BG0997 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The docstring's "A subject with a further `:` segment names no unit" (engagement\_floor.py:526-527) is still pinned for a segment before the id or inside it, not after it. The reviewer mutant matching the first segment (`sdlc_md.norm_id(tail.split(":")[0]) == want`) passes test\_engagement\_floor.py (113 passed, 15 subtests). Run alone, it waives BG-01JQK3F8 on a waiver recorded through `decisions.record_waiver` as `rule:engagement-floor:BG-01JQK3F8:ac2`, where the real code does not. Add that row to test\_a\_per\_unit\_waiver\_holds\_only\_while\_accepted\_and\_naming\_one\_whole\_id (test\_engagement\_floor.py:441).; RULINGS: Round two over a88149b8 (HEAD), judged on `_unit_waiver` and its WaiverTests only. "`_unit_waiver`'s status filter (engagement\_floor.py:524) is pinned only against a superseded row" CLOSED: a revisited row is pinned, the docstring now says so, and the round-one mutant that skips only superseded rows is KILLED. "The docstring's "A subject with a further `:` segment names no unit"" MOVED: the extra segment before the id is pinned and the round-one last-segment mutant is KILLED. A segment after the id is the same gap, and my round-one finding named only the before-the-id shape, so it is carried above as a finding. The author's survivor, the anchor removed, is equivalent as recorded: a prefix met past position 0 leaves its own closing colon in the tail, and the further-segment guard then refuses it. Verify dry-run 2/2 pass.

## Steps to Reproduce

1. Read the round 2 REJECT of BG0997 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0997 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The docstring's "A subject with a further `:` segment names no unit" (engagement\_floor.py:526-527) is still pinned for a segment before the id or inside it, not after it. The reviewer mutant matching the first segment (`sdlc_md.norm_id(tail.split(":")[0]) == want`) passes test\_engagement\_floor.py (113 passed, 15 subtests). Run alone, it waives BG-01JQK3F8 on a waiver recorded through `decisions.record_waiver` as `rule:engagement-floor:BG-01JQK3F8:ac2`, where the real code does not. Add that row to test\_a\_per\_unit\_waiver\_holds\_only\_while\_accepted\_and\_naming\_one\_whole\_id (test\_engagement\_floor.py:441).
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG0997 AC1 still passes: A waiver recorded as rule:engagement-floor:BG-01JQK3F8 waives the unit BG-01JQK3F8 and no other unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::WaiverTests::test_per_unit_waiver_exempts_only_that_unit_for_a_dashed_v3_id
  - **Verified:** yes (2026-11-23)
- [ ] **AC3** BG0997 AC2 still passes: A waiver recorded with the dash already removed still waives that same unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::WaiverTests::test_per_unit_waiver_exempts_only_that_unit_for_a_dashed_v3_id_and_the_dashless_form
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
