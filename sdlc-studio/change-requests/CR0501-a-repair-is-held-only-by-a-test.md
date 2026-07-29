# CR-0501: A repair is held only by a test its own author wrote, and repairs land in guards - mutation must be mandatory on a fix, not optional on a sprint

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01KYNKDP: round one applied 39 mutants to the sprint's work and 8 SURVIVED; round two applied 21 to the nine stop-ship repairs and 9 SURVIVED. Not one of the thirteen defects was caught by a green suite - 5,163 tests passing at the time. Six repairs reverted cleanly with no test going red, and two of the tests written to hold them asserted something other than what they claimed.
> **Date:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** RUN-01KYNKDP close review; human; v1

## Summary

This project has a two-role rule for SIGN-OFF and no rule at all for REPAIRS, which is backwards. The sign-off covers work that has already been reviewed. A repair is the least-reviewed code in a sprint, and it lands in guards.

RUN-01KYNKDP is the demonstration, twice. Five independent reviewers found nine stop-ships, all invisible to 5,163 passing tests. Those nine were repaired, self-reviewed, committed green. A second review of the REPAIRS then rejected again: 9 of 21 mutants survived, six repairs reverted with no test going red, and two of the repairs had introduced fresh defects - an orphaned process group and a file-descriptor leak - in the code written to fix a hang.

The pattern is not that reviews find bugs. It is narrower and more actionable: **a test written by the author of a fix asserts the shape of the fix.** It passes because it was written from the same mistaken model that produced the code. Concretely, from this run: a test named for a raising branch called the real helper against a path that does not raise, so it exercised a different branch and never asserted the refusal; a test asserted `_OUTPUT_CAP` equalled a hardcoded literal, which it did, so it could not tell the two apart; a test hand-wrote the `killed_by` key it then asserted; and two guards were redundant for their single fixture, so neither was independently held.

Every one of those was found by MUTATION and by nothing else. Mutation is the only instrument here that asks the author's test a question the author did not choose.

The existing lesson already says this - "a test written by the author of a fix asserts the shape of the fix; mutation is how you find out" - and it is carried as advice. Advice is what gets skipped at 4am on the last batch, which is precisely when the repairs are written.

## Impact

Repairs are written fastest, latest, and under the most pressure, and they land in the most load-bearing code in the project: guards, release paths, and the mechanisms that decide whether other checks run. RUN-01KYNKDP shipped a fail-open release guard, a false suite verdict, an orphaned process group and eight deleted test classes in exactly that window - every one green, every one self-reviewed.

The cost of the instrument is small and measured: a scoped mutation run over one unit's changed lines is seconds to a couple of minutes. The cost of not running it, this sprint alone, was two full adversarial review rounds and a close that took longer than the sprint.

A consuming project inherits the lesson and no mechanism, which means it inherits the failure.

## Acceptance Criteria

- [ ] A unit typed as a repair - a bug fix, a review-residue fix, a regression fix - requires mutation evidence over its own changed lines before it can reach a terminal status.
- [ ] The gate is the SURVIVOR count over those lines, not merely that a mutation run happened; a surviving mutant refuses the transition and names the mutant and its line.
- [ ] The demand is made at the transition, beside the existing verification-depth requirement, so the claim and its evidence are checked in one place.
- [ ] Feature work is not subjected to the same bar, so the requirement stays affordable and does not get switched off wholesale.
- [ ] A repair with no mutatable surface RECORDS that fact rather than being silently exempt.
- [ ] The shipped doctrine states the rule that a fix's author is not sufficient evidence for that fix, so a consuming project inherits the mechanism and not only the lesson.

## Steps to Reproduce

1. Read RETRO0083's carried lessons: the rule is already stated as a lesson.
2. `grep -rn 'mutation' .claude/skills/sdlc-studio/templates/core/definition-of-done.md` - no clause requires it of anything.
3. Read the round-two review of commit 06c806d7: 9 of 21 mutants survived nine self-reviewed repairs.
4. `transition.py set <bug> Fixed` demands a verification DEPTH; it demands no mutation evidence, so a repair whose test cannot fail reaches Fixed.

## Proposed Fix

Make the instrument mandatory where the evidence says it is needed, and nowhere else - a blanket mutation requirement on all work would be ignored for cost.

1. **Scope it to REPAIRS.** A unit whose change is a fix for a review finding, a bug, or a regression carries a mutation run over the lines it changed. New feature work keeps the current, cheaper bar. The distinction is already on the artefact: a bug and a review-residue unit are typed.
2. **The gate is the SURVIVOR count, not the run.** A repair reaching Fixed with a surviving mutant over its own changed lines is refused, naming the mutant and the line. Running mutation and ignoring the result is the failure mode a mere run-it requirement produces.
3. **Wire it into the transition, where the claim is made.** `transition -> Fixed` already refuses without a verification depth. This is the same shape of demand and the same place to make it.
4. **State the rule in the shipped doctrine**, not only as a carried lesson: a test written by the author of a fix asserts the shape of the fix. A consuming project inherits the lesson file but nothing that acts on it.
5. **Keep the escape honest.** A repair with no mutatable surface - a documentation fix, a constant - records that it had none, rather than being silently exempt. An absence stated is evidence; an absence assumed is the gap this closes.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | RUN-01KYNKDP close review | Raised |
