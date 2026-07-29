# BG0419: Four delivered units are held by verifiers that pass with the delivered mechanism removed, and two whole production surfaces are one edit from inert

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Evidence:** Two independent sign-off reviews, each executing mutants with purged bytecode and diff-confirmed patches. US0555: a break at the first refusing action step loses the second refusal and all 547 sprint tests stay green. US0559: deleting the close's SOLE cost-report call site survives all 547. US0557: removing the up-front refusal leaves its own three tests green - they assert the postcondition, which also holds when every write is attempted and every write fails. US0532: its named verifier passes with the ENTIRE corpus cache removed, ratio 1.95 both ways, because the harness makes a fixed twelve lookups regardless of workspace size and then discards the only discriminating signal by taking a ratio.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Four units delivered mechanisms that work and tests that cannot tell whether they work.

The shapes are distinct and worth separating, because the repair differs:

**A surviving mutant on the headline property.** US0555's whole deliverable is that the dry run reports EVERY refusal rather than stopping at the first. Its test asserts that preflight blockers all survive into the report and that the first action step appears. Both hold when the dry run stops at the first refusing action step. The test verifies pre-existing preflight enumeration - behaviour the story's own docstring credits as already there - and not the behaviour the story built.

**A production surface with no test reaching it.** US0559's cost reporting has exactly one production call site, and deleting it changes nothing. No test asserts the string the close prints. Its AC2, that the cost is recorded on the run rather than only printed, is verified by a test that fabricates the ledger itself and never runs a close.

**A postcondition standing in for an ordering.** US0557's code is correct. Its test asserts that no unit was written, which is equally true of the failure it is meant to exclude - nineteen attempted writes that all fail for the same missing argument. The observed kill came incidentally from an unrelated crash in another class, not from a designed assertion.

**A ratio that divides out the only signal.** US0532's harness makes twelve lookups whether the workspace holds twenty units or forty, so reads are linear in N with or without the memo and only the constant differs - by 9x. Taking a ratio discards exactly that. Its docstring asserts a quadratic growth its own fixture cannot produce. The reviewer proved the one-line repair: make the sweep's lookups scale with N and the same threshold reads 1.95 shipped against 3.90 removed.

The common cause is one sentence: **each test asserts the pure helper, or the postcondition, or a derived ratio - never the production path or the ordering the acceptance criterion actually claims.**

## Steps to Reproduce

1. US0555: patch a break after the first refusing action step in the dry run; run the sprint suite. Green.
2. US0559: delete the close's cost-report call site; run the sprint suite. Green.
3. US0557: remove the early return after the missing-argument refusal; run its own test class. Green.
4. US0532: disable the corpus cache entirely; run its named verifier. Ratio 1.95, passes.

## Proposed Fix

1. **Assert the delivered property, not its neighbour.** US0555 needs a fixture refusing at two action steps and an assertion that BOTH appear - the reviewer's fixture already does this and the assertion simply does not read it.
2. **Reach the production path.** US0559 needs a test that runs a close and asserts the cost line appears in its output, and an AC2 test that runs a close rather than writing the ledger by hand.
3. **Assert the ordering, not the outcome.** US0557 needs the write path instrumented so the test can say no write was ATTEMPTED, which is the claim.
4. **Make the discriminating signal survive.** US0532's sweep must scale its lookups with N, so the ratio carries the memo's effect instead of dividing it out. One line, proven by the reviewer.
5. **Mutation is the acceptance test for a fix in this class.** Each repair above is only done when the mutant that motivated it dies.

## Acceptance Criteria

- [ ] US0555's test refuses at two action steps and asserts both are reported; the break-at-first mutant reddens it.
- [ ] US0559 is covered by a test that RUNS a close and asserts the cost line in its output; deleting the call site reddens it.
- [ ] US0557 asserts no write was ATTEMPTED, not merely that none landed; removing the early return reddens it.
- [ ] US0532's sweep scales its lookups with the unit count, so its threshold discriminates: removing the corpus cache reddens it.
- [ ] Each repair is accepted only when the mutant that motivated it is demonstrated to die, recorded with the unit.

## Impact

Every one of these units is Done-adjacent with a green verifier, and four of them are held by nothing. Two mechanisms - the dry run's completeness and the close's cost report - are one edit from silently inert, in a project whose central claim is that its records mean something.

This is the third consecutive review round to find the same shape, and it is now the most repeated defect class in the project's history. That is the argument for the mutation gate on repairs being mandatory rather than advisory: a green suite has not once been sufficient evidence here.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
