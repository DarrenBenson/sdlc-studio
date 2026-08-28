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

So the invariant is stated PER ROW, not once. AC1's fixture carries a run-attributed unit
and no repair or override; AC3's carries a repair and an override and NO run-attributed
unit; AC4's carries BOTH - at least one genuinely unaccounted terminal unit, so the
corrected advisory has a line to lose, AND at least one accounted-for unit, so the two
surfaces contradict each other at HEAD. Built from one shared fixture, AC1 and AC3 would be
the same test twice; built without the second half, AC4's two surfaces agree BY SILENCE and
deleting the printed line changes nothing.

## Acceptance Criteria

- [ ] **AC1** Given a fixture carrying a run-attributed unit and NO repair or override, so `owed` and `unaccounted` differ on that limb alone, when `status`'s advisory runs, then it reports nothing owed - it reads the accounted-for set the renderer reads, not the raw one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_run_attributed_unit_is_not_announced_as_owed
- [ ] **AC2** Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the key cannot be satisfied by silencing the advisory outright
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_real_owed_close_is_still_reported_on_both
- [ ] **AC3** Given a fixture carrying a close-time REPAIR and a recorded OVERRIDE and NO run-attributed unit, when the advisory runs, then it reports nothing owed. `blocking()` subtracts three limbs, and a fix special-casing the run-attributed one alone passes every other row here while still contradicting the exit code on a fully-overridden set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_repaired_or_overridden_unit_is_not_announced_as_owed
- [ ] **AC4** Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then the ID SET each claims is owed is the SAME. A boolean - both say a close is owed - is green at HEAD on this fixture, because both surfaces are non-silent there, so it pins nothing; and no advisory line at all counts as DISAGREEMENT, not as agreement. At HEAD the two sets differ, after the fix they match, and under the mutant `status` names nothing while `detect` names one. The bug is two commands printing contradictory sentences, so a library test cannot see it. the two commands spell it differently - `close_owed.py --root X detect`, but `status.py hint --root X`, because `status`'s parser attaches `--root` to each subparser
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_the_two_commands_agree_when_both_are_run

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/status.py`, revert the advisory to reading `report['owed']` - the unsplit set the renderer never used, which is the defect itself and the only edit AC1's run-attributed fixture can see | Given a fixture carrying a run-attributed unit and NO repair or override, so `owed` and `unaccounted` differ on that limb alone, when `status`'s advisory runs, then it reports nothing owed - it reads the accounted-for set the renderer reads, not the raw one |
| AC2 | in `.claude/skills/sdlc-studio/scripts/status.py`, remove the close-owed advisory altogether, so the surface is silent for the real case as well as the false one | Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the key cannot be satisfied by silencing the advisory outright |
| AC3 | in `.claude/skills/sdlc-studio/scripts/status.py`, re-implement the subtraction in the advisory and subtract `run_attributed` ALONE, leaving repairs and overrides in the owed set - the careless implementer's actual error, which AC1's fixture cannot see because it carries no repair or override | Given a fixture carrying a close-time REPAIR and a recorded OVERRIDE and NO run-attributed unit, when the advisory runs, then it reports nothing owed. `blocking()` subtracts three limbs, and a fix special-casing the run-attributed one alone passes every other row here while still contradicting the exit code on a fully-overridden set |
| AC4 | in `.claude/skills/sdlc-studio/scripts/status.py`, remove the advisory line from what `cmd_hint` and `cmd_status` PRINT while leaving `close_owed_advisory` correct - the lane mutant a library row cannot see, since every in-process criterion calls the helper directly | Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then the ID SET each claims is owed is the SAME. A boolean - both say a close is owed - is green at HEAD on this fixture, because both surfaces are non-silent there, so it pins nothing; and no advisory line at all counts as DISAGREEMENT, not as agreement. At HEAD the two sets differ, after the fix they match, and under the mutant `status` names nothing while `detect` names one. The bug is two commands printing contradictory sentences, so a library test cannot see it. the two commands spell it differently - `close_owed.py --root X detect`, but `status.py hint --root X`, because `status`'s parser attaches `--root` to each subparser |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
