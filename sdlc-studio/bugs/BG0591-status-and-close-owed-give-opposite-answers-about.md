# BG0591: status and close_owed give opposite answers about the same units

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
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

Have `status.py` call the same reader `close_owed detect` uses and print what it returns, including the raised-and-delivered exemption, rather than computing its own answer from the terminal set. If status must stay cheap and cannot afford the full detection, it should say what it did NOT check rather than assert a conclusion the fuller reader contradicts. Pin it with a fixture holding one unit raised and delivered inside a closed run and assert BOTH commands agree - a test that only asserts status's own wording would pass on the defect.

## Acceptance Criteria

- [ ] **AC1** Given a unit raised and delivered inside a run whose close already ran, when `status` and `close_owed detect` are both run, then neither reports a close owed for it
- [ ] **AC2** Given a unit that genuinely owes a close, when both are run, then both report it - the fix must not silence status for the real case
- [ ] **AC3** Given the two commands, when the owed set is computed, then it comes from one reader rather than two

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
