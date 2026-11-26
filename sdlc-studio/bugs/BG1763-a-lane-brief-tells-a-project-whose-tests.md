# BG1763: A lane brief tells a project whose tests are not pytest to list mutants with pytest selectors, and the runner can run nothing else

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1763.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T23:54:49Z

## Summary

In the website repository (Astro, vitest), all 16 lane briefs of RUN-01M8AA0S (2026-11-25) told the builder, in the author self-check, to list each mutant in EDITS.json "its test a pytest selector" and run `mutation.py run --edits`, though every unit's Affects test files were tests/*.test.ts. critic.py:3230-3233 writes that instruction for any unit with a test file, whatever the project's runner; mutation.py builds `python -m pytest -q -p no:cacheprovider <test>` for every edit (scripts/mutation.py:2278-2280), and its --runner flag only shapes a suggested command (:2422-2423). So every builder and every reviewer applied, ran and restored each mutant by hand and handed in <unit>-mutants.json; none produced the -mutation-edits.json report the brief names, and the runner's own apply-then-watch-red check (LC-001) never ran for the batch.

## Steps to Reproduce

In a project whose tests are vitest (tests/*.test.ts) and whose criteria have no pytest Verify selector, run `sprint.py lane brief --units <id>` and read step 2 of the AUTHOR SELF-CHECK; then run `mutation.py run --edits EDITS.json` with a mutant whose test is a vitest file.

## Proposed Fix

Let the runner take the project's test command (a configured runner, or the unit's own Verify command) in place of pytest, or have the brief say plainly that a non-pytest project runs its mutants by hand into MUTANTS.json, with no pytest selector asked for.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects test files are vitest and whose criteria name no pytest selector, then its lane brief does not ask for a pytest selector: it names a runner that can run the unit's tests, or the hand-run MUTANTS.json route. Fails on: "its test a pytest selector" in that brief.
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_critic.py::NonPytestSelfCheckTests::test_a_vitest_unit_is_not_asked_for_a_pytest_selector

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | orchestrator | Filed |
| 2026-11-25 | orchestrator (D0635) | Groomed for run twenty-seven: AC1's Verify names the test the fix writes first (a manual line cannot move a bug to Fixed), and Affects narrow to the brief (critic.py and its test); the runner taking a non-pytest command is the larger fix the Proposed Fix offers and is not in this unit |
| 2026-11-26 | orchestrator | Affects names `changelog.d/BG1763.md`: a change to the brief every builder reads ships with its fragment (LL0004); the grooming of D0635 left it out |
| 2026-11-26 | orchestrator | Round one: both seats rejected. Affects add `sprint.py`, whose lane hand-in list still names the runner report for a unit pytest cannot run; both seats raised it as pre-existing and no open bug covers it, so it is fixed in the unit (D0561). The qa seat's REJECT (3dfaf7ecbc9e-5450bf71, a dotted-stem `.spec.py` test taken for one pytest runs) could not be recorded beside the product seat's, since the ledger numbers both seats' verdicts as one sequence until per-seat rounds land (US1032, US1033); its finding is in the repair |
