# US1064: The seat record charges a later bug to the approval that missed it, by the narrow rule

> **Status:** Draft
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, changelog.d/US1064.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1062
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, who files the bugs a review missed
**I want** the seat record to charge a later bug to the APPROVE that missed it only when the bug cites the unit, shares a file with it and cites three ids or fewer, to exclude bugs filed because review did not converge, and to show a bug the approver had itself raised as non-blocking as approved over its own finding
**So that** a seat learns from its real misses and not from every bug that mentions a unit it once passed

## Acceptance Criteria

- **AC1:** Given RETRO0001 dated 2026-10-01 and RETRO0002 dated 2026-10-08, US0001 approved by `Lena Marsh (product)` on 2026-09-20 with Affects `scripts/a.py`, and bugs dated within the window: BG0002 (cites US0001, affects scripts/a.py), BG0003 (cites US0001, affects only docs/x.md), BG0004 (affects scripts/a.py, cites nothing), BG0006 (cites US0001 and four other ids, affects scripts/a.py), BG0007 ('US0001 did not converge in review'), and BG0005 dated 2026-09-25, when `retro.py seats --id RETRO0002` runs, then product's record lists BG0002 alone as a miss, with its basis.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_later_bug_is_charged_by_the_narrow_rule
- **AC2:** Given product's APPROVE of US0001 carrying a non-blocking finding and BG0008, in the window, whose Evidence names US0001's product review, when `retro.py seats` runs, then product's record lists BG0008 as approved over its own finding, not as a miss.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_bug_the_approver_raised_reads_approved_over_its_own_finding
- **AC3:** Given US0003 approved by qa in an earlier run and BG0009, in this retro's window, charged to it by the narrow rule, when `retro.py seats --id RETRO0002` runs on a batch qa did not review, then qa appears in the record with BG0009.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_seat_outside_the_batch_is_charged_its_misses

## Notes

- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: any of the shared-file test, the citation test, the three-id cap, the carried exclusion or the previous-retro window dropped
- AC2 must fail on: every later bug read as a miss, so a seat is told it missed what it found and chose to pass
- AC3 must fail on: the record limited to seats that reviewed this batch, so a miss found while the seat sat a run out is never charged
- Serves: Maya Okafor #3.
- D0364 ruling 3. Re-counted at HEAD over the 514 units approved since 2026-08-01, counting US, BG and CR ids above Revision History and excluding the bug's own id: 140 have a later bug citing them, 81 one that also shares an Affects path, 34 one that also cites three ids or fewer (the panel's 34; the draft's 24 counted the bug's own id). The panel's sample of the narrow set: five real misses, four the approver's own non-blocking findings, one not a defect of the unit.
- Carried exclusion: a bug whose title reads '<unit> did not converge in review' (critic.py:1620, 19 bugs here), read from the bug so every clone agrees.
- Own finding: the bug's Evidence field names the unit's review or its verdict file (BG0896: 'US0975 QA review round 2'), and the approver's row carries a non-blocking finding. Matching shared `file:line` instead finds 1 of the 34; the Evidence field finds the panel's examples.
- Precision bar, set before re-measuring (LL0036): on a fresh 12-pair sample from this repository's narrow set, drawn by a fixed seed and excluding the panel's 10 pairs, at least 8 lines labelled 'miss' must be misses of the approved unit, judged by a seat other than the builder and recorded in the story's Resolution. Below the bar the story is reworked, not shipped: the label becomes 'possible miss' and the operator rules.
- Window: each bug is charged once, in the retro whose window holds its creation date (after the previous retro's Date), to whichever seat approved the cited unit in any run; such a seat appears in the record even if it reviewed nothing in the batch (answers the panel's per-seat window point without a stored per-seat record).

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1062 (Draft)
- Its own precision bar (8 of 12 sampled 'miss' lines must be real) has to be measured and recorded before it ships, or the label becomes 'possible miss'
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
