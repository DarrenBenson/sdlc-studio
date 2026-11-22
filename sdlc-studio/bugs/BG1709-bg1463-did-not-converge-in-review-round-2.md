# BG1709: BG1463 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, changelog.d/BG1463.md, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/reference-retro.md
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T17:17:27Z

## Summary

BG1463 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair says "the post-dates reason reads a unit's earliest dated seated approval" (changelog.d/BG1463.md:9, and the commit's "tests pin the post-dates reason reading the earliest dated seated approval"). Tests now pin "earliest" but not "seated". Taking the days from every approval rather than only the seated ones, `for r in approvals` in place of `for r in seated` (retro.py:1791), SURVIVES all 14 tests in test\_retro\_seat\_misses.py. No fixture puts an approval naming no seat, dated before the bug, beside a seated approval dated after it. Probed alone through `retro.py seats`: on US0012 a reviewer naming no seat approved on 2026-09-10, qa approved on 2026-10-08, and the bug was created on 2026-10-06. HEAD says "the approval of US0012 post-dates the bug: its earliest dated approval is 2026-10-08, after the bug was created on 2026-10-06", which matches reference-retro.md:141's "a seat first approved it after the bug's day". The mutant says "no seat's latest verdict on US0012 on or before 2026-10-06 approves it", and the suite stays green. Add that pair of approvals to a fixture and assert the post-dates reason; RULINGS: Prior finding "The rule that the post-dates reason reads the earliest dated approval has no test" is CLOSED. test\_the\_post\_dates\_reason\_reads\_the\_earliest\_dated\_approval kills `days[-1]` (my replay: 1 failed, 12 passed), and the "seated" half it leaves open is the new finding above. Prior finding "AC2's no-seat reason is pinned only for a unit whose every row names no seat" is CLOSED. The US0011 fixture, a seated qa REJECT beside an APPROVE naming no seat, kills `seated` taken from every live row (my replay: 1 failed, 7 passed). Prior finding "reference-retro.md:133-134 still gives the pre-fix scope" is CLOSED. Affects now declares the page, and reference-retro.md:139-142 lists all five reasons `_uncharged_reason` and `seat_misses` give. Each was checked against the code and the probes. "Only a REJECT does" holds because the live ledger holds only APPROVE (1565) and REJECT (633) verdicts. verify\_ac run --id BG1463 --dry-run reports 3 of 3 criteria passing. Claim inventory for the repair: the changelog's seated-REJECT-beside-a-seatless-approval claim is TRUE and pinned. Its earliest-dated-seated-approval claim is TRUE by execution but only half pinned (the finding). Its "the retro reference now says which bugs are named" is TRUE. tools/lint-style.sh passes. The author's 10 recorded mutants all replay killed. My own pass: 3 mutants, 2 killed (the two round-one survivors above) and 1 survived, re-probed alone through the CLI as described. A remark that is not a finding: test\_retro\_seat\_misses.py:279, the AC3 docstring from round one, is a 165-character line where two sentences ran together in a missed rewrap. No lint here enforces a line length. The other reference-retro.md, retro.py and test\_retro.py hunks in the brief's diff belong to BG1059, BG1332, BG1436, BG1465, BG1482 and BG1483 (commits 4d46f94e and 1736835c) and were not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1463 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1463 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair says "the post-dates reason reads a unit's earliest dated seated approval" (changelog.d/BG1463.md:9, and the commit's "tests pin the post-dates reason reading the earliest dated seated approval"). Tests now pin "earliest" but not "seated". Taking the days from every approval rather than only the seated ones, `for r in approvals` in place of `for r in seated` (retro.py:1791), SURVIVES all 14 tests in test\_retro\_seat\_misses.py. No fixture puts an approval naming no seat, dated before the bug, beside a seated approval dated after it. Probed alone through `retro.py seats`: on US0012 a reviewer naming no seat approved on 2026-09-10, qa approved on 2026-10-08, and the bug was created on 2026-10-06. HEAD says "the approval of US0012 post-dates the bug: its earliest dated approval is 2026-10-08, after the bug was created on 2026-10-06", which matches reference-retro.md:141's "a seat first approved it after the bug's day". The mutant says "no seat's latest verdict on US0012 on or before 2026-10-06 approves it", and the suite stays green. Add that pair of approvals to a fixture and assert the post-dates reason
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1463 AC1 still passes: Given a bug in the retro's window whose Escaped-via unit has only a live REJECT, when `retro.py seats` runs, then the bug is named in uncharged with a reason saying no review approved the unit. Fails on: the bug appearing on no line of the record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_escaped_via_unit_with_only_a_reject_is_named_uncharged
- [ ] **AC3** BG1463 AC2 still passes: Given a bug whose Escaped-via unit's live APPROVE names no seat, when `retro.py seats` runs, then the bug is named in uncharged with a reason saying the approval names no seat. Fails on: an approval with no seat dropping the bug silently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_escaped_via_unit_whose_approval_names_no_seat_is_named_uncharged
- [ ] **AC4** BG1463 AC3 still passes: Given one bug whose Escaped-via unit was approved only after the bug's Created day, and beside it a bug whose unit a seat approved before it, when `retro.py seats` runs, then the first is named in uncharged with a reason saying the approval post-dates the bug, and the second is charged to the seat and absent from uncharged. Fails on: the late approval dropping the bug, or a charged bug also listed as uncharged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_an_approval_after_the_bug_is_named_uncharged_and_a_charged_bug_is_not

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
