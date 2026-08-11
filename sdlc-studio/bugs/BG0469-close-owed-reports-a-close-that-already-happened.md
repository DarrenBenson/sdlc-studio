# BG0469: close_owed reports a close that already happened: a unit raised and Fixed inside a run never joins that run's recorded batch

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

**Id collision, recorded not hidden.** Commit `edb9fdf0` (2026-07-31, "a census threshold that
failed as a surprise, not a signal") carries the subject `fix(BG0469)` but filed no BG0469
artefact, so `next_id` correctly saw the id as free and allocated it to THIS finding. Two
unrelated pieces of work therefore answer to BG0469: that commit's census-ratchet change, and
this bug. `git log -S BG0469` will mislead. Nothing is renumbered, because no tool renumbers an
artefact and hand-editing `_index.md` is forbidden here. The commit's work is unfiled ad-hoc
delivery of the same class as BG0467 and BG0468 - see the inherited-debt note on RETRO0086.

## Summary

12 of the 14 units `close_owed` flagged as owing a close had been delivered inside RUN-01KYPZ1G or RUN-01KYTKA1 and were simply absent from the retro Batch line. A finding filed against an open run becomes a tracked unit but is never added to the run's batch, so the close records fewer units than the run delivered and `close_owed` then demands a close for work whose close already ran. The batch should accrete a unit raised in-batch that reaches terminal before the close, or `close_owed` should attribute by the run window it already reads.

## Steps to Reproduce

1. python3 .claude/skills/sdlc-studio/scripts/`close_owed.py` detect
2. Observe 14 units reported as owing a close.
3. For BG0424-BG0428 and BG0451, read 'Raised-in-batch: 2026-07-29T15:35:33Z' - inside RUN-01KYPZ1G's 2026-07-29T13:02:54Z to 2026-07-30T22:48:16Z window, recorded in .local/run-archive/RUN-01KYPZ1G.json.
4. For BG0456/BG0458/BG0461/BG0464/BG0465, git log --diff-filter=A shows first commits inside RUN-01KYTKA1's window; RETRO0086's own prose names them as its review repairs.
5. Neither retro's Batch line contains any of them, so the detector is right that no retro accounts for them and wrong that a close is owed.

## Proposed Fix

Accrete into `run_state.batch` when a finding filed with a run open reaches terminal before that run closes, so the close counts what the run delivered; or have `close_owed` attribute a terminal unit to the run whose recorded window contains its Raised-in-batch stamp before declaring a close owed. Either way the operator must not be hand-correcting Batch lines against git timestamps.

## The repair chosen, and why

The bug offers two. **Attribution in `close_owed` was chosen over accretion into `run_state.batch`.**

Accretion has to fire at the moment a unit reaches terminal, which is `transition`'s write path:
a second writer into run state on the hottest status path in the tool, for a fact this module
can DERIVE from records it already opens - the archived run windows and the close telemetry.
A derived answer cannot drift from its source; a second writer can, and this repository's own
doctrine says so about every other pair of readers it has had to reconcile. Accretion also only
helps runs that have not closed yet, so the standing backlog would still need hand-correcting.

Nothing is forgiven. An attributed unit stays in `owed` and is named with the run whose close
already accounts for it; what changes is that it leaves `unaccounted`, which is what the exit
code and the headline are derived from.

## Acceptance Criteria

- [x] **AC1: a unit raised and delivered inside a closed run is attributed to it.**
  - **Given** a terminal unit whose `Raised-in-batch` stamp falls inside an archived run's window
    and whose recorded terminal date is on or before that run's end
  - **When** `close_owed` judges it
  - **Then** it is reported as attributed to that run and leaves `unaccounted`, so no second
    close is demanded for work one already accounted for. The mutant is deleting the attribution
    call and keeping the old split.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_a_unit_raised_and_delivered_inside_a_closed_run_is_attributed_to_it
  - **Verified:** yes (2026-08-11)

- [x] **AC2: a unit raised outside every window is still unaccounted.**
  - **Given** a terminal unit raised long before any recorded run opened
  - **When** it is judged
  - **Then** it stays unaccounted, because attributing on the terminal date alone would credit
    the standing backlog tail the baseline exists for and turn the ledger into a rubber stamp.
    The mutant is dropping the raise test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_a_unit_raised_outside_every_window_is_still_unaccounted
  - **Verified:** yes (2026-08-11)

- [x] **AC3: a unit delivered after the run ended is not credited to it.**
  - **Given** a unit raised inside a run's window but recorded terminal after that run closed
  - **When** it is judged
  - **Then** it stays unaccounted, because the run that only FILED it delivered nothing of it and
    its retro cannot have described it. The mutant is attributing on the raise alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_a_unit_delivered_after_the_run_ended_is_not_credited_to_it
  - **Verified:** yes (2026-08-11)

- [x] **AC4: a run that never completed its close credits nothing.**
  - **Given** an archived run whose outcome is a mid-flight stop rather than a completed close
  - **When** a unit raised and delivered inside its window is judged
  - **Then** nothing is attributed, because that run filed no account and crediting it would
    forgive work no retro described. The mutant is accepting any outcome that is not `running`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_a_run_that_never_completed_its_close_credits_nothing
  - **Verified:** yes (2026-08-11)

- [x] **AC5: a stamp that names no moment attributes nothing.**
  - **Given** a unit whose `Raised-in-batch` reads `none open - raised outside a delivery batch`
  - **When** it is judged against a run window
  - **Then** nothing is attributed. Nothing guards the stamp's SHAPE - a letter sorts after every
    digit, so such a token can never fall inside an ISO window - and this is the test that says
    so, rather than a branch no input could reach. A shape guard was written, measured, found
    unfalsifiable, and removed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_a_stamp_that_names_no_moment_attributes_nothing
  - **Verified:** yes (2026-08-11)

- [x] **AC6: the shipped command names the run that already accounts for it.**
  - **Given** an attributed unit
  - **When** `close_owed detect` runs through its own command entry point
  - **Then** the page names the unit and the run id and exits 0, because an operator who is not
    told WHICH close already ran is left with the reading that sent them hand-correcting `Batch`
    lines. The mutant is attributing in the report and printing nothing about it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::RunAttributedTests::test_the_shipped_command_names_the_run_that_already_accounts_for_it
  - **Verified:** yes (2026-08-11)

## Verification evidence

Functional. Five mutants executed, `__pycache__` purged and each child run under `python3 -B`,
each anchor asserted to occur exactly once, source restored byte-identical afterwards:

| Mutant | Result |
| --- | --- |
| delete the attribution call and keep the old split | killed |
| attribute on the terminal date alone, ignoring the raise | killed |
| drop the terminal-date test and attribute on the raise alone | killed |
| accept any run outcome that is not `running` | killed |
| attribute in the report and print nothing about it | killed |

The terminal date is REQUIRED, not merely respected. An unknown date satisfying the window test
would credit a unit filed in one run and fixed two runs later to the run that only filed it, and
an attribution made on absent evidence is the silent "none owed" this module exists to prevent.

A seventh mutant - guard the stamp's shape before comparing it - was written and measured
SURVIVED, and was then removed rather than pinned. It cannot change any answer: the corpus's
non-time stamps all begin with a letter, and a letter sorts after every digit, so such a token
never falls inside an ISO window. Shipping it would have been a branch no input reaches, which
is the defect the sibling repair in this same batch is about.

**Known limitation, stated rather than discovered later.** The windows are read from
`sdlc-studio/.local/run-archive/`, which is the record the bug's own reproduction cites and which
is NOT tracked. A clone without it attributes nothing and behaves exactly as before - the
over-reporting direction, which is the one this ledger fails towards by design.

**The first version of this paragraph was wrong, and an independent pass measured it.** It said
this workspace's `.local/` was empty and offered an unchanged count as evidence that the archive
was the cause. The archive holds 44 run records, 28 of them carrying both bounds and a completed
outcome. The count is genuinely unchanged here, for a different reason: every unit currently owed
carries `Raised-in-batch: none open - raised outside a delivery batch`, so there is no in-window
raise stamp to attribute by. Fed the 56 units that DO carry a timestamped stamp, the derivation
attributes four of them to `RUN-01KYY52D`. The repair is not inert; it has nothing to bite on in
the set that is currently owed. Stating the cause wrongly is worse than not stating it, because
the next reader inherits a false explanation for a real number - which is the whole failure mode
this bug is about, one level up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | sdlc-studio | Filed |
| 2026-08-11 | sdlc-studio | Criteria groomed to name their mutants; repair chosen and recorded; fixed |
