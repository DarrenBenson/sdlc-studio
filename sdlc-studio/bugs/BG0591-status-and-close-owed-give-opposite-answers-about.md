# BG0591: status and close_owed give opposite answers about the same units

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
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

Most fixtures below must make `owed` and the accounted-for set DIFFER. On the real tree
today they are equal - the same ids, with `run_attributed` and `close_time_repairs` both
empty - so the two surfaces agree by an empty subtraction rather than by structure. A fixture
built the obvious way reproduces that coincidence, the criterion passes on unfixed code, and
no mutant can kill it.

`blocking()` subtracts TWO limbs, not three: `unaccounted` is `owed` minus the
run-attributed units minus the close-time repairs, and a recorded override is a LABEL on a
unit already inside the repairs limb rather than a limb of its own. So AC3's two fixtures are
both built through the repairs path, one with an override recorded against it and one
without, and a fix special-casing either alone fails the other.

The invariant is stated PER ROW. AC1's fixture carries a run-attributed unit and no repair or
override. AC3's carry a repair, one of them overridden, and no run-attributed unit. AC5's
carries BOTH an accounted-for unit and at least one genuinely unaccounted terminal unit, so
the two surfaces contradict each other at HEAD and the id sets can be compared rather than
found equally empty.

AC4 is the deliberate exception and must NOT satisfy the rule above: its fixture has an EMPTY
units limb and an outstanding velocity row, which is the only shape where `is_owed` is true
on the velocity limb alone. An advisory narrowed to the units key goes silent there while the
command exits 1, and no fixture obeying the difference rule can show it.

## Acceptance Criteria

- [ ] **AC1** Given a fixture carrying a run-attributed unit and no repair or override, so the raw owed list and the accounted-for set differ on that limb alone, when `status`'s close advisory runs, then it announces nothing owed - it reads the accounted-for set the renderer and the exit code read, not the raw one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_run_attributed_unit_is_not_announced_as_owed
  - **Verified:** yes (2026-09-09)
- [ ] **AC2** Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the advisory's key cannot be satisfied by silencing it outright
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_real_owed_close_is_still_reported_on_both
  - **Verified:** yes (2026-09-09)
- [ ] **AC3** Given a fixture carrying a close-time REPAIR, and a second carrying a repair the retro OVERRIDES by id, when the advisory runs on each, then neither announces anything owed. An override is a label on a unit already inside the repairs limb rather than a limb of its own, so both fixtures must be built through the repairs path or the criterion tests one thing twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_repaired_or_overridden_unit_is_not_announced_as_owed
  - **Verified:** yes (2026-09-09)
- [ ] **AC4** Given a fixture whose ONLY outstanding item is a retro with no velocity row, when the advisory runs, then it still announces a close is owed. `is_owed` returns true on the velocity limb alone, so an advisory narrowed to the units limb goes silent on exactly the fixture where the command exits 1 - the same two-surfaces-disagree defect this bug is about, moved rather than fixed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_a_velocity_only_fixture_still_announces_a_close
  - **Verified:** yes (2026-09-09)
- [ ] **AC5** Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then the id set each NAMES as holding the close is the same set. `detect` enumerates only the raw owed list today, so there is nothing to compare against and the comparison must be made possible before it can be made
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CloseOwedAgreementTests::test_the_two_commands_name_the_same_blocking_set
  - **Verified:** yes (2026-09-09)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/status.py, revert the advisory's source to `report["owed"]` | Given a fixture carrying a run-attributed unit and no repair or override, so the raw owed list and the accounted-for set differ on that limb alone, when `status`'s close advisory runs, then it announces nothing owed - it reads the accounted-for set the renderer and the exit code read, not the raw one |
| AC2 | in .claude/skills/sdlc-studio/scripts/status.py, delete the advisory's emit so nothing is ever announced | Given a unit that genuinely owes a close, when both surfaces run, then both report it - the paired control, so narrowing the advisory's key cannot be satisfied by silencing it outright |
| AC3 | in .claude/skills/sdlc-studio/scripts/close_owed.py, drop the `close_time_repairs` subtraction from `blocking`, returning the raw owed list as `units` | Given a fixture carrying a close-time REPAIR, and a second carrying a repair the retro OVERRIDES by id, when the advisory runs on each, then neither announces anything owed. An override is a label on a unit already inside the repairs limb rather than a limb of its own, so both fixtures must be built through the repairs path or the criterion tests one thing twice |
| AC4 | in .claude/skills/sdlc-studio/scripts/status.py, narrow the advisory's predicate to the `units` key of `blocking`, dropping the velocity limb | Given a fixture whose ONLY outstanding item is a retro with no velocity row, when the advisory runs, then it still announces a close is owed. `is_owed` returns true on the velocity limb alone, so an advisory narrowed to the units limb goes silent on exactly the fixture where the command exits 1 - the same two-surfaces-disagree defect this bug is about, moved rather than fixed |
| AC5 | in .claude/skills/sdlc-studio/scripts/close_owed.py, delete the line that names the blocking set, leaving only the raw owed enumeration | Given one fixture root, when `status` and `close_owed.py detect` are BOTH run as subprocesses, then the id set each NAMES as holding the close is the same set. `detect` enumerates only the raw owed list today, so there is nothing to compare against and the comparison must be made possible before it can be made |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
| 2026-09-09 | Claude Fable 5.1 | Delivered in c3e58d78. The advisory reads the accounted-for set the renderer and the exit code read, and `detect` names the blocking set so a second reader has something to compare against. Five criteria |
| 2026-09-10 | Claude Opus 5 | Delivery review, all three seats REJECT, and AC5 was not merely unpinned - it was FALSE of the delivered code. `status`'s advisory truncated its named set at five ids with an ellipsis while `detect` named the whole set, so the two surfaces disagreed about the SET the moment a sixth unit blocked, while both still agreed a close was owed. Zero units block on this repository today, which is why nobody met it. The truncation is gone: the count still leads the line, and a reader who acts on the list now gets all of it. AC5's own verifier compared `close_owed.render` against `close_owed.blocking` - one module talking to itself - on a one-story fixture that could never reach past five, so it could not have seen either fault. It drives BOTH shipped commands as subprocesses over an eight-unit fixture now, asserts detect's owed exit so the fixture is known to reach the state, and compares the two named sets. Restoring the truncation reddens it |
