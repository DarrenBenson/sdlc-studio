# BG0666: an UNAUTHORED Test Plan row is exempt from the quality guard an authored one must pass, so leaving the placeholder buys a clean derive

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** verify_ac.py:3711 `if mutant != _TESTPLAN_PLACEHOLDER:` guards the `testplan_row_faults` call. Measured on BG0663, 2026-09-11: the table held the placeholder three times, `derive --dry-run` reported `unchanged - 3 row(s) already match its 3 criteria, and 0 authored mutant(s) were kept`, and the reviewer's brief rendered the placeholders back. Writing the ledger's three real mutants in produced exit 2 with five faults.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.py testplan derive` refuses a mutant cell that names no path from the unit's `Affects`, carries no edit verb, or restates more than 60% of its own criterion. It skips all of those checks for a row still equal to `_TESTPLAN_PLACEHOLDER`: the loop reads `if mutant != _TESTPLAN_PLACEHOLDER:` before calling `testplan_row_faults`.

So a unit whose author ran `derive` and never wrote the mutants passes every check, reports `N row(s) for N criteria`, and hands a reviewer a plan that names nothing. Authoring the real mutants is what risks a refusal. The incentive points the wrong way, and the state is invisible from the command's own output.

Found by an independent test-plan reviewer on BG0663, whose table held the placeholder three times while the real mutants existed only in the gitignored ledger - in no clone, no diff and no brief. The seat's own words: the placeholder is why nobody saw this.

## Steps to Reproduce

1. Run `verify_ac.py testplan derive --unit <id>` on a unit with no authored mutants: it writes `{{name the production change this test must fail on}}` per criterion and exits 0.
2. Run it again: `unchanged - N row(s) already match its N criteria, and 0 authored mutant(s) were kept`. Nothing says the rows name nothing.
3. Now author a real mutant that names no `Affects` path: it is REFUSED at exit 2.
4. So the unauthored row passes a check the authored one fails.

## Proposed Fix

Count the placeholder rows and REPORT them - by criterion - wherever a plan is read as complete: `derive`'s own summary, the brief `critic.py brief` renders, and the terminal transition's plan gate. A placeholder is a legitimate intermediate state while a unit is being written, so this is a report rather than a refusal at `derive`; what must not happen is a unit reaching review or a terminal status with a plan that names nothing while every surface calls it present.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Test Plan rows are all the placeholder, when `testplan derive` runs, then its summary NAMES the criteria whose mutant is unauthored and how many there are. Exit 0 is kept: a placeholder is where a unit legitimately starts, and refusing it would refuse the command that writes it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::PlaceholderRowsAreReportedTests::test_derive_names_the_criteria_whose_mutant_is_unauthored
- [ ] **AC2** Given the same unit, when a reviewer's brief is assembled for it, then the brief states that those criteria name no mutant. The brief is what a reviewer judges from, and one that renders a placeholder as though it were a plan is what produced the rejection this bug was filed from
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::PlaceholderRowsAreReportedTests::test_the_brief_says_a_plan_names_no_mutant
- [ ] **AC3** Given a unit whose rows ARE authored, when either surface runs, then neither reports a placeholder. The paired control: a checker that always warns is one nobody reads, and it would fire on every unit mid-authoring
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::PlaceholderRowsAreReportedTests::test_an_authored_plan_is_not_reported_as_placeholder

## Impact

A test plan is the load-bearing half of a criterion - it is what says the criterion can fail. A plan of placeholders reads as complete to `derive`, to the reviewer's brief, and to the test-plan gate, so the review that exists to check the mutants is handed nothing to check. It cost a REJECT and a re-review on BG0663.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | Claude Opus 5 | Filed |
| 2026-09-11 | Claude Opus 5 | Duplicate warning against BG0597 answered: they are distinct. BG0597 was derive DESTROYING an authored row when a criterion carried more than one, and it is Fixed. This is the opposite direction - an UNAUTHORED row is exempt from the quality guard an authored one must pass, so leaving the placeholder is the cheaper path. They share two files and a vocabulary, which is what the 43% similarity measured |
