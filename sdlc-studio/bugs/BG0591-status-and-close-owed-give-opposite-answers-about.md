# BG0591: status and close_owed give opposite answers about the same units

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Depends on:** BG0616
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
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

## Fixture invariant

Every fixture below must make `owed` and `unaccounted` DIFFER. On the real tree today they
are equal - the same ids, with `run_attributed` and `close_time_repairs` both empty - so the
two surfaces agree by an empty subtraction rather than by structure. A fixture built the
obvious way reproduces that coincidence, every criterion passes on unfixed code, and no
mutant can kill it. `blocking()` subtracts THREE limbs - run-attributed units, close-time
repairs and recorded overrides - and a fix special-casing one satisfies a plan exercising
only that one.

## Acceptance Criteria

- [ ] **AC1** Given a run-attributed unit that `blocking()` accounts for, so `owed` and `unaccounted` differ, when `status`'s advisory runs, then it reports nothing owed - it reads the accounted-for set the renderer reads, not the raw one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_run_attributed_unit_is_not_announced_as_owed
- [ ] **AC2** Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the key cannot be satisfied by silencing the advisory outright
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_real_owed_close_is_still_reported_on_both
- [ ] **AC3** Given a unit accounted for by a CLOSE-TIME REPAIR or a RECORDED OVERRIDE rather than by run attribution, when the advisory runs, then it reports nothing owed. `blocking()` subtracts three limbs, and a fix special-casing the run-attributed one alone passes every other row here while still contradicting the exit code on a fully-overridden set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_repaired_or_overridden_unit_is_not_announced_as_owed
- [ ] **AC4** Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then their lines agree about what is owed. The bug is two commands printing contradictory sentences, so a library test cannot see it. `--root` is a global argument and precedes the subcommand
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_the_two_commands_agree_when_both_are_run

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/status.py`, narrow the advisory's subtraction to the run-attributed limb alone, keeping close-time repairs and overrides in the owed set, so it agrees with the renderer for one of the three cases and not the others | Given a run-attributed unit that `blocking()` accounts for, so `owed` and `unaccounted` differ, when `status`'s advisory runs, then it reports nothing owed - it reads the accounted-for set the renderer reads, not the raw one |
| AC2 | in `.claude/skills/sdlc-studio/scripts/status.py`, remove the close-owed advisory altogether, so the surface is silent for the real case as well as the false one | Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the key cannot be satisfied by silencing the advisory outright |
| AC3 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, change `blocking()` to return `report['owed']`, so the renderer and the advisory move together back to the unsplit set and the disagreement is hidden rather than repaired | Given a unit accounted for by a CLOSE-TIME REPAIR or a RECORDED OVERRIDE rather than by run attribution, when the advisory runs, then it reports nothing owed. `blocking()` subtracts three limbs, and a fix special-casing the run-attributed one alone passes every other row here while still contradicting the exit code on a fully-overridden set |
| AC4 | in `.claude/skills/sdlc-studio/scripts/status.py`, move the advisory's report read above the run-state load, so the two commands compute from the tree at different moments while both use the corrected key | Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then their lines agree about what is owed. The bug is two commands printing contradictory sentences, so a library test cannot see it. `--root` is a global argument and precedes the subcommand |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
