# BG0422: The code is mostly right and the EVIDENCE is what fails: five consecutive REJECTs, and four fifths of the findings were the author's own tests unable to fail

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (a documentation unit with NO mutatable surface, recorded rather than left implicit. Its evidence is the guard set that reads these files: lint-style, check_budgets, check_links and markdownlint all green. The budget guard refused a first draft at 768 lines against a 741 ceiling; the content moved to `best-practices/testing.md`, which is its right home under AC2, rather than the ceiling moving to meet it)
> **Affects:** .claude/skills/sdlc-studio/best-practices/testing.md, .claude/skills/sdlc-studio/reference-agentic-lessons.md, .claude/skills/sdlc-studio/reference-test-best-practices.md, .claude/skills/sdlc-studio/lessons/_index.md
> **Evidence:** RUN-01KYPZ1G: five independent adversarial reviews, five REJECTs, roughly 30 findings over 86 delivered points. Categorised: about 20 were a test that could not fail (parser bypassed by a hand-built Namespace; a string supplied by the function's own def line; a fixture shape the product never produces; a bug used to test a Review status bugs do not have; an exception TYPE where two guards raise the same type; the helper tested instead of the caller FIVE separate times; assertRegex over a whole file). Three were the fix in the wrong place. Two were a reader requiring a key no writer produces. Two were a filtered test run hiding 17 then 27 failures.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Five reviews, five REJECTs, and the production code was right in most of them. That distinction is the whole finding: this is not a code-quality problem, it is an EVIDENCE problem, and the two need different remedies.

The dominant class - about two thirds of every finding - is a test that cannot fail. Not a test that is weak, or slow, or badly named: a test that passes identically whether the feature is present or absent. Eight distinct mechanisms produced one, and they are worth naming separately because each needs a different habit to catch:

Bypassing the surface under test (a hand-built argparse.Namespace, so a required-flag defect was invisible). Asserting text that the code under test supplies for free (a def line containing the call site's own string). Using a fixture shape the product cannot produce. Using a TYPE that lacks the state being tested. Asserting an exception type where two different guards raise the same one. Testing the helper rather than the caller - five times, against a project whose own recorded scar says a library test is not a lane test. Applying an assertion to a whole file so an unrelated sentence satisfies it. And a positive control written against an input that was already in the passing state.

What makes this actionable is that every one is visible BEFORE the mutation run, if the question is asked in the right order. The habit that catches all eight is: NAME THE MUTANT BEFORE WRITING THE TEST. Write down the change to production code the test must fail on, then write the test to fail on it. If the mutant cannot be named, there is nothing to test yet.

Two smaller classes are structural and a design review WOULD catch them, which is worth knowing because it is cheap: a guard placed in the library while the unguarded read stayed in the command, and a reader changed to require a key no writer emits. Both are answered by one question each - which surface does the user actually invoke, and who writes what I am reading.

## Steps to Reproduce

1. Read the five review records in sdlc-studio/reviews/sprint-review-record.md for RUN-01KYPZ1G.
2. Categorise the findings: the count is roughly 20 vacuous tests, 3 misplaced fixes, 2 dead paths, 2 filtered test runs.
3. Note that in almost every case the production repair was correct and the evidence for it was not.

## Proposed Fix

1. **Name the mutant before writing the test, in the docstring.** State the production change the test must fail on. A vacuous test then becomes visible on the page rather than only under a mutation run - and if the mutant cannot be named, the test is not yet a test.
2. **Test the surface the user invokes.** The command, not the helper it delegates to. Five findings in one sprint were this single mistake.
3. **For every reader added, name its writer.** A one-line check that closes the dead-path class.
4. **The full suite before every commit, never a filtered subset.** Two commits in this sprint would have landed 17 and 27 failures.
5. **Review BEFORE the commit, not after.** This sprint built a mechanism stating that the close asserts coverage rather than performing the review, and then repeatedly committed ahead of the review anyway. The mechanism was right; the sequencing ignored it.
6. **A pre-implementation design review is worth its cost for the structural classes only.** Say so honestly rather than proposing it as a general cure: it would have caught about a third of these and cannot see a test that does not exist yet.

## Acceptance Criteria

- [x] The lesson is recorded in the cross-project store with all eight mechanisms named individually, because each needs a different habit to catch.
- [x] The named-mutant-first rule is stated in the shipped best-practice guidance, so a consuming project inherits the habit and not only the observation.
- [x] The rule that a test exercises the surface the user invokes is stated with the five-in-one-sprint count as its evidence.
- [x] The honest limit of a pre-implementation design review is recorded - it addresses the structural classes and cannot see an unwritten test - so it is not adopted as a general cure.
- [x] The review-before-commit sequencing is stated as a rule, since this sprint built the mechanism for it and then did not follow it.

## Impact

The containment worked - four stop-ships and about 30 defects were caught and none shipped - but the rate is the problem. Every finding cost a review round, a repair, and a re-review, and several repairs introduced fresh defects of their own.

More importantly this is the class the project's whole argument rests on. A skill whose claim is that its records mean something cannot have its own evidence be the weakest part of it, and a consuming project inherits these habits through the lessons store and the best-practice guides rather than through the code.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Filed |
