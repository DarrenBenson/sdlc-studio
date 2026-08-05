# CR-0533: A production hunk whose reversion leaves the suite green is uncovered: make the gate prove coverage rather than assume it

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .githooks/pre-commit, tools/, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** Two independent adversarial seats on RUN-01KZ9315, 2026-08-05, each briefed with critic.py brief and each working from the pinned range 7b9a399a..HEAD. 71 mutants of their own devising between them, 12 survivors, 5 blocking findings. Each of the five reproduced by the reporting seat with the exact pytest invocation and the surviving count.
> **Date:** 2026-08-05
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Reverting a production hunk and re-running the suite is a mechanical test of whether that hunk is covered. If the suite stays GREEN with the change undone, no test in the tree depends on it - the criterion it claims to satisfy is pinned by nothing. This is checkable by a script and is currently checked by nobody.

It is proposed on measured evidence rather than on principle. RUN-01KZ9315 shipped twelve units, and its author applied 45 self-chosen mutants of which 45 died. Two independent review seats then applied 71 mutants of their own devising and 12 survived, producing five blocking findings plus one live regression. Every one of the five was a hunk whose reversion leaves the suite green.

The generative defect is narrower than 'insufficient testing', and naming it is what makes it mechanisable. The author wrote each MUTANT from the criterion, before the code - the discipline LL0050 asks for, and it worked: no criterion-named mutant survived. But each ASSERTION was written afterwards, from the implementation's actual output. A mutant only ever kills through an assertion, so the discipline covered half the loop. The survivors all have the same shape: an assertion describing what the code returns rather than what the criterion promises. `assertNotEqual(rc, 0)` where the criterion says each refusal names its own reason; one field asserted of a four-field derivation; two of four keys on a summary; the un-migrated table tested and the migrated one not.

A hunk-reversion check cannot be satisfied by an assertion that merely restates the implementation, because reverting the implementation is precisely what it does.

## Impact

Who: every project using the skill, and this one first. What breaks today: a unit can pass `verify_ac`, pass its own named mutants, pass the full suite and pass the pre-commit gate while carrying criteria that nothing pins. The failure is invisible until an independent seat goes looking, which costs a review round and, on this evidence, finds several at once.

Measured cost of the current state: the defect class caught BEFORE the code cost 55k tokens on this project; caught after, roughly 400k. Two seats on RUN-01KZ9315 consumed about 390k tokens between them to find five instances the author's own 45-mutant pass had missed.

What this does not fix: it says nothing about whether an assertion is CORRECT, only that something depends on the hunk. A test that reverts red and still asserts the wrong property is out of scope, and mutation remains the tool for that.

What breaks if this is done carelessly: put on every commit it doubles a gate already over budget and gets disabled, which is strictly worse than not shipping it - the ceiling has already been raised once from 120s to 380s for exactly that reason.

## Acceptance Criteria

- [ ] The check exists as a command and reports per hunk: given a unit and a base ref, it reverts each hunk of the unit's declared Affects in turn and reports GREEN (uncovered) or RED (covered), naming the hunk and the criterion whose Verify line should have covered it. Mutant: report per FILE rather than per hunk - a file with one covered hunk reads as covered, which is the granularity the five findings would each have slipped through.
- [ ] Every one of the five measured instances from RUN-01KZ9315 is reported by it. This is the regression corpus and it is named on the criterion, not chosen at implementation time: `sprint_report._sprint_cost_line`, critic `record_signoff`'s disjointness raise, critic `_ensure_trailing_column`'s pad, critic `cmd_record`'s tier arguments, `sprint_report.operator_summary`'s carried and filed. Mutant: implement against a fixture instead - the corpus rows go unreported.
- [ ] A hunk that is legitimately uncovered is ANSWERABLE, and the answer is recorded rather than assumed. A comment-only or logging hunk is not a defect, so the check reports and the answer is a decision somebody made; only an UNANSWERED report blocks. Mutant: refuse blindly - the check is switched off within a day, which is what happened to the gate budget ceiling twice.
- [ ] It runs at the BATCH BOUNDARY, not per commit, and the placement is a recorded decision. The commit gate is already over its 380s budget on every commit of the sprint that produced this evidence; per-hunk reversion multiplies the suite cost by the hunk count. Mutant: wire it into pre-commit - measure the gate before and after and watch it exceed its ceiling.
- [ ] The report distinguishes an uncovered hunk from a hunk whose verifiers could not RUN. A verifier that errors is not evidence of coverage and must never be reported as RED. Mutant: treat a non-zero exit as covered - a broken verifier certifies the hunk it could not judge, which is this project's recurring false-green class.

## Steps to Reproduce

1. Take any unit from RUN-01KZ9315 whose criteria were reported PASS by `verify_ac` and whose named mutants were all shown to kill.
2. Revert one production hunk from that unit's diff - not a mutation, the plain absence of the change.
3. Run the unit's own declared verifiers, then its module's suite.
4. Observe GREEN on five of the twelve units. Measured instances, each reproduced by an independent seat: the whole cost derivation in `sprint_report` reduced to four constants passes 124 tests; the adversarial-seat disjointness guard in critic deleted passes 1,114; the sign-off migration pad changed to the one value its criterion forbids passes 406; `cmd_record` dropping its tier arguments passes 359; the operator summary's carried and filed lists emptied passes 124.

## Proposed Fix

Add a coverage-by-reversion check and give it a lane.

MECHANISM. For each hunk in the unit's declared Affects, produce the tree with that hunk reverted, run the union of the unit's declared verifiers and the modules those verifiers live in, and record GREEN or RED. A GREEN reversion is the finding: the hunk is uncovered, and the report names the hunk and the criterion whose Verify line was supposed to cover it.

WHY THIS AND NOT MORE MUTATION. Mutation asks whether a test can distinguish a WRONG implementation from a right one, and its weakness is that the author picks the mutants - the selection bias LL0044 records, applied here to the mutation set rather than to a fixture. Reversion asks whether a test can distinguish the implementation being THERE from it being ABSENT, and there is nothing to select: the hunks are given by the diff. The two are complementary, and reversion is the cheaper and the less gameable of them.

SCOPE IT OR IT WILL BE SWITCHED OFF. The gate is already OVER its 380s budget on every commit of this sprint (383s, 445s, 392s, 416s). Reversion is per-hunk and would multiply that, so it belongs at the BATCH BOUNDARY - before review is requested - and not on every commit. That placement is also where it does the most good: it turns 'the review discovers the tests are vacuous' into 'the author is told before asking'.

A hunk whose reversion is green may still be legitimate - a pure comment, a docstring, a log line. The check must therefore report and be answerable, with the answer recorded, rather than refuse blindly. An unanswered report is what blocks.

## Recommendation

Build the reporting command first and run it over the RUN-01KZ9315 diff before wiring any lane, because the number it returns on real work decides whether the lane is worth its cost. The five known instances are the acceptance corpus. Only once it reports those five and no false positive on the comment-only hunks in the same diff should it be given a boundary lane. That order is deliberate: this project has twice shipped a guard whose yield was asserted rather than measured, and CR0510's own claim-drift lane is currently ADVISORY for exactly this reason - a new blocking check on a gate already over its ceiling earns its place on a number rather than on an argument.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Raised |
