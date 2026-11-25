# BG1743: BG1296 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, changelog.d/BG1296.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T00:21:06Z

## Summary

BG1296 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the normalised-id comparison the repair adds to `_resume` is pinned by no test, and the author's self-check rules its survivor equivalent on a false premise (lanes.py:1207-1209, changelog.d/BG1296.md:12): the replayed mutant "resume compares units as exact strings" survives, answered "Equivalent: land only lands a unit with an artefact (its preflight refuses a self-check for none)", but a unit no artefact carries lands without a self-check and writes a land record. Probe on the test\_lane\_land\_resume fixture at 7c294458a: `sprint.py lane land --units us9999` (no artefact, no self-check, the hook refusing the commit) stops at the commit step with record units `us9999`, and `--resume --units US9999` after the hook is cleared takes it up (rc 1, the landing finishing with no self-check recorded)\; with that mutant applied once the same resume is refused (rc 2, "was of lane-us0101 for us9999: resume it as it was begun"). The fragment's "units are compared by their normalised id" therefore rests on a branch no test reaches, the one case where it differs from the `display_id` mapping. A resume test under an id no artefact carries, or dropping the comparison and the sentence, closes it. No open bug covers it; RULINGS: Round one's "`--resume` cannot take up a landing whose record spells a unit otherwise than its artefact": CLOSED. My round-one probe re-run at 7c294458a (a hook-refused first landing, its record's units set to the base's `us0101`, the hook cleared) resumes under `--units us0101` with rc 0, and a landing begun as `us0101` resumes under `US0101` with rc 0. test\_a\_landing\_recorded\_under\_another\_spelling\_resumes\_by\_either and test\_a\_resume\_keeps\_the\_brief\_a\_record\_spelt\_otherwise\_says\_was\_written pin the `display_id` reading of the record's units, owners and briefed list (the author's three mutants of it replay killed). `verify_ac.py run --id BG1296 --dry-run` ac=2 pass=2, and both criteria still hold by their tests and round one's four mutants. The finding above is the only one, and it is a missing pin on a branch whose behaviour is right, not a wrong behaviour.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1296 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1296 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the normalised-id comparison the repair adds to `_resume` is pinned by no test, and the author's self-check rules its survivor equivalent on a false premise (lanes.py:1207-1209, changelog.d/BG1296.md:12): the replayed mutant "resume compares units as exact strings" survives, answered "Equivalent: land only lands a unit with an artefact (its preflight refuses a self-check for none)", but a unit no artefact carries lands without a self-check and writes a land record. Probe on the test\_lane\_land\_resume fixture at 7c294458a: `sprint.py lane land --units us9999` (no artefact, no self-check, the hook refusing the commit) stops at the commit step with record units `us9999`, and `--resume --units US9999` after the hook is cleared takes it up (rc 1, the landing finishing with no self-check recorded); with that mutant applied once the same resume is refused (rc 2, "was of lane-us0101 for us9999: resume it as it was begun"). The fragment's "units are compared by their normalised id" therefore rests on a branch no test reaches, the one case where it differs from the `display_id` mapping. A resume test under an id no artefact carries, or dropping the comparison and the sentence, closes it. No open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1296 AC1 still passes: Given `US0101-qa.txt` left by an earlier landing, when `sprint lane land --units us0101` lands a repair with no self-check, then `US0101-qa.txt` is removed, the note is written as `US0101-qa.none`, and no file named for the lower-case spelling exists under the briefs directory. Fails on: `us0101-qa.none` written beside the earlier round's `US0101-qa.txt`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_lower_case_unit_id_names_the_canonical_brief_and_note
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** BG1296 AC2 still passes: Given that landing, under `review.author_self_check: report`, when `sprint lane accept --unit US0101` is given an APPROVE, then it is refused for want of a brief and nothing is recorded, and `--unit us0101` is refused the same way. Fails on: the verdict recorded against the earlier round's brief.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_accept_reads_the_brief_by_the_normalised_unit_id
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
