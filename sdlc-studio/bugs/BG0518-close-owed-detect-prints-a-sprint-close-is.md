# BG0518: close_owed detect prints "a sprint close is owed" on the run where it exits 0, so its headline contradicts its own verdict

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Evidence:** Observed on the live tree at commit fcdfe206 while orienting for Run A on 2026-08-04, immediately after recording BG0517's override in RETRO0093. Both overrides present, `real exit=0`, headline unchanged from the pre-override run.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

When every flagged unit carries a recorded `Close-repair-override`, `close_owed detect` discharges the ledger and exits 0 - but the first line it prints is still the unconditional refusal text, quoted here as a block because it contains its own code span:

```text
close owed: 2 delivery unit(s) reached terminal since the baseline with no retro accounting for them - a sprint close is owed (run the retro, then `gate --require-retro RETROxxxx`).
```

The headline is composed from the flagged set before the override pass runs, and nothing downgrades it once the overrides discharge it.

A gate reads the exit code and is correct. Every other reader - an operator, an agent orienting at session start, the close chain's own advisory in `status.py` - reads the headline and concludes a close is owed when none is. The instruction the line gives is also wrong: running the retro and `gate --require-retro` is work that is not needed and, on a run with no batch to account for, cannot be honestly done.

This is the inverse of BG0507, which writes fail=1 after a green verdict: there the verdict is wrong and the text right; here the verdict is right and the text wrong. Both are one report disagreeing with itself, and the same lane owns them.

Distinct from BG0469, which is about a unit raised in-batch never joining the recorded batch - a defect in WHICH units are flagged, not in how a discharged set is described.

## Steps to Reproduce

1. Reach a state where every unit `close_owed detect` flags carries a `Close-repair-override` in a retro. On the tree at 2026-08-04 this is BG0511 and BG0517.
2. Run `close_owed.py detect > out.txt; echo $?` - redirected, not piped, so the exit code is the tool's.
3. Observe: exit is 0 (discharged, nothing owed) while line 1 of out.txt states that a sprint close is owed and names the command to discharge it.

## Proposed Fix

Compose the headline AFTER the override pass, from the set that actually remains owing. When that set is empty the line should state what is true - that N units reached terminal since the baseline and all N are accounted for by recorded overrides - and it should not name a discharge command for a ledger that is already discharged. Derive the wording from the same predicate the exit code uses, so the two cannot disagree; do not restate the verdict beside it (LL0042).

## Acceptance Criteria

- [ ] On a fully-overridden set, `close_owed detect` makes no claim that a close is owed and names no discharge command. With BG0511 and BG0517 both overridden the headline states what is true: N units reached terminal since the baseline and all N are accounted for
- [ ] The headline and the exit code come from ONE predicate. Not two expressions that happen to agree - derived, so they cannot drift (LL0042). The test asserts the pairing across both states, so a future branch that reports one without the other reddens it
- [ ] The owing case is untouched: a unit with no override still yields the refusal text AND a non-zero exit. This fix must not buy a quiet tool by silencing a real refusal
- [ ] The mutant is the composition order: computing the headline before the override pass reddens the new test
- [ ] Read the exit code by redirection, never through a pipe, in both the test and any manual check - a piped `$?` reports the pager's status and has twice reported a red suite as green in this repo

## Impact

Misleads every reader that is not an exit code, including the session-start orientation AGENTS.md requires. An agent that believes a close is owed either performs a close with no batch to account for, or spends a round working out that the tool is wrong about itself.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
