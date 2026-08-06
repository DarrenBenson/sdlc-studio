# CR-0525: a unit's test plan is written and reviewed BEFORE its code, because reviewing the test is cheaper than reviewing the code

> **Status:** Complete
> **Decomposed-into:** EP0207
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** human
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Priority:** Critical
> **Type:** Improvement
> **Size:** L

## Summary

RUN-01KYZKY5 delivered 45 units and then five independent passes returned 27 REJECT. Splitting them: roughly 13 were a broken feature, and roughly 14 were a CORRECT feature whose verifier could not fail - a test asserting the SHAPE of the change (is the symbol present, does the string appear) rather than its behaviour. Reviewers demonstrated it by mutation ten-plus times, twice by deleting the entire feature and watching every declared verifier stay green.

All of it was found AFTER the code existed, which is the most expensive moment to find it. The run spent five review passes to learn that fourteen tests could not fail.

The capability to prevent this is ALREADY BUILT AND UNUSED. `test-spec` is a shipped artefact type with three commands that read one - `verify_ac ts-check`, `epic-ts`, `scaffold-matrix`. The whole repository contains TWO test specs. This run wrote none. `AGENTS.md` already carries the rule, `best-practices/testing.md#name-the-mutant-first`: state the production change the test must fail on, before writing it. Nothing gates it.

So this is LL0027 exactly: a rule that matters, stated in the file everyone loads, with the tooling built, and no command in the path anyone walks that asks for it.

## Impact

The economics are the argument. A test plan is a short document naming, per criterion, the production change the test must fail on. Reviewing it costs one cheap pass before any code exists. Reviewing the code costs a full adversarial pass per unit, and when it finds a vacuous verifier the repair means re-opening work already believed finished - which is what turned this run from delivered into not-closeable.

It also fixes the defect at its source rather than detecting it. `lane-check` and the source-grep detectors find a weak test after it is written; naming the mutant first means the weak test is not written, because a criterion whose mutant cannot be named is a criterion nobody knows how to check.

## Acceptance Criteria

- [ ] A unit reaching delivery without a test plan is REFUSED by the command that starts the work, not reported at the close - the plan names, per criterion, the production change the test must fail on
- [ ] The test plan is reviewed as its own artefact by an independent seat BEFORE the code is written, and that review is recorded the way a code review is
- [ ] The plan is derived from the unit's acceptance criteria by the shipped tooling, not hand-authored, so a criterion cannot be silently missing from it
- [ ] At delivery, each planned mutant is EXECUTED against the shipped test and its death recorded - a plan that was written and never checked is the same paperwork problem one level up
- [ ] A criterion whose mutant cannot be named is refused at grooming, since nobody yet knows what would falsify it
- [ ] The cost is measured over one run and reported: passes spent on test-plan review versus passes spent on code review, so the claim that this is cheaper is a number rather than an assertion

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
