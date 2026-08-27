# BG0591: status and close_owed give opposite answers about the same units

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Depends on:** BG0616
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_owed.py detect` and `status.py` read the same fact and disagree. For a unit raised AND delivered inside a run whose close already ran, `detect` says in terms: `No close is owed for these. Add them to that run's retro Batch if you want the account to read completely; nothing is blocked either way` - and its headline reports `close owed: none`. `status.py`, for the same two ids in the same tree, printed `advisory: a sprint close is owed: 2 delivery unit(s) reached terminal with no retro (BG0579, BG0580) - run the retro`. One says nothing is owed and names the optional tidy-up; the other names ceremony that is not owed. AGENTS.md's rule is one definition, never a second, and `status` is the command a fresh session is ordered to run FIRST - so the wrong half of this disagreement is the half read earliest.

## Steps to Reproduce

Observed 2026-08-17 at bfd51161. `close_owed.py detect` printed `close owed: none. 2 unit(s) reached terminal since the baseline and every one is accounted for` followed by the raised-and-delivered exemption naming BG0579 and BG0580. In the same tree `status.py` printed `advisory: a sprint close is owed: 2 delivery unit(s) reached terminal with no retro (BG0579, BG0580)`. Resolved for these two ids by accreting them to RETRO0102's Batch line, which is the optional tidy-up `detect` suggested - so the disagreement is currently latent rather than visible, and will return with the next unit delivered inside a closed run.

## Proposed Fix

**The diagnosis this bug was filed with has already shipped, and the defect has not.** Both surfaces
now call one reader, `close_owed.owed`. They disagree about which KEY they take from it: the
renderer and `is_owed` read `blocking(report)["units"]`, which subtracts run-attributed units,
close-time repairs and recorded overrides, while `status.close_owed_advisory` reads the unsplit
`report["owed"]`. So `close_owed.py detect` can print `every one is accounted for` and exit 0 while
`status` prints that a close is owed, about the same units, in the same tree.

Have `status` read the blocking key. One line, and the two surfaces then answer one question with
one number - which is what "call the same reader" was always trying to buy.

ORDER: land BG0616 FIRST. It changes WHO is owed, by counting a triage-closure named in a retro as
covered; this bug changes WHICH KEY status reads. BG0616 alone empties the current corpus witness
while leaving the run-attributed disagreement standing, and this bug alone makes the two surfaces
agree that BG0599 and BG0602 are owed - which is the wrong answer.

## Acceptance Criteria

- [ ] **AC1** Given a unit raised and delivered inside a run whose close already ran, when `status` and `close_owed detect` are both run, then neither reports a close owed for it - the two surfaces agree, which is the whole claim
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_closed_run_owes_nothing_on_either_surface
- [ ] **AC2** Given a unit that genuinely owes a close, when both are run, then both report it - the paired control, so narrowing the key cannot be satisfied by silencing the advisory outright
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_real_owed_close_is_still_reported_on_both
- [ ] **AC3** Given a run-attributed unit that `blocking()` accounts for, when `status`'s advisory reads the report, then it reads `blocking(report)['units']` as the renderer does, not the unsplit `report['owed']` - both surfaces already call one function, and the disagreement is which key each takes from it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_status_reads_the_blocking_key_not_the_raw_owed_set

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
