# US1064: The seat record charges a later bug to the approval that missed it, by the narrow rule

> **Status:** Done
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py, changelog.d/US1064.md
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1062
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, who files the bugs a review missed
**I want** the seat record to charge a later bug to the APPROVE that missed it only when the bug cites the unit, shares a file with it and cites three ids or fewer, to exclude bugs filed because review did not converge, and to show a bug the approver had itself raised as non-blocking as approved over its own finding
**So that** a seat learns from its real misses and not from every bug that mentions a unit it once passed

## Acceptance Criteria

- **AC1:** Given RETRO0001 dated 2026-10-01 and RETRO0002 dated 2026-10-08, US0001 approved by `Lena Marsh (product)` on 2026-09-20 with Affects `scripts/a.py`, and bugs dated within the window: BG0002 (cites US0001, affects scripts/a.py), BG0003 (cites US0001, affects only docs/x.md), BG0004 (affects scripts/a.py, cites nothing), BG0006 (cites US0001 and four other ids, affects scripts/a.py), BG0007 ('US0001 did not converge in review'), and BG0005 dated 2026-09-25, when `retro.py seats --id RETRO0002` runs, then product's record lists BG0002 alone as a miss, with its basis.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_later_bug_is_charged_by_the_narrow_rule
  - **Verified:** yes (2026-11-15)
- **AC2:** Given product's APPROVE of US0001 carrying a non-blocking finding and BG0008, in the window, whose Evidence names US0001's product review, when `retro.py seats` runs, then product's record lists BG0008 as approved over its own finding, not as a miss.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_bug_the_approver_raised_reads_approved_over_its_own_finding
  - **Verified:** yes (2026-11-15)
- **AC3:** Given US0003 approved by qa in an earlier run and BG0009, in this retro's window, charged to it by the narrow rule, when `retro.py seats --id RETRO0002` runs on a batch qa did not review, then qa appears in the record with BG0009.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_misses.py::SeatMissTests::test_a_seat_outside_the_batch_is_charged_its_misses
  - **Verified:** yes (2026-11-15)

## Notes

- Run thirteen grooming (D0479):
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 4 (an escaped defect traced to the approval that missed it); End goal 2.
  - Dependency US1062 real (extends `retro.py seats`). Missing: Affects omits `test_retro_seat_evidence.py` (shares the seats fixtures it extends). Precision bar (8 of 12 sampled 'miss' lines judged real by another seat) is a pre-ship measurement, not a Verify line: record it in the story notes before Done, or ship the label as 'possible miss' per its triage. Edits retro.py in the region US1062 landed; same wave as US1067's retro.py learnings verb (different functions; rebase).
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
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
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, notes |
