# BG0648: a criterion written outside the Acceptance Criteria section is executed by verify_ac and invisible to the brief, the transition gate, validate and the sprint report

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 3; plan rows 5; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 5 (AC1 row 0, AC1 row 1, AC2 row 0, AC2 row 1, AC3 row 0); entry point 0 of 3 criteria through the shipped CLI, 0 in-process; 3 undetermined (the named node could not be isolated) | fp 668f33b08f6c ]]
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.parse_story` collects every ACn block wherever it sits in the artefact, so `verify_ac` run and the AC fingerprint counted six criteria on BG0643 while critic.py brief (its own regex over the Acceptance Criteria section) rendered five, and `sdlc_md.criteria_section`'s consumers - transition.py's ticked-or-executable gate, `sprint_report.py`, validate.py - skipped the sixth. An AC6 appended under Impact at delivery on 2026-09-04 therefore passed conformance and validate, was executed and mutation-checked, and was absent from the brief every seat and the reviewer of record was handed. Two readers of one document disagree about what it contains, and nothing refuses the shape. Found by the product seat in BG0643's delivery review round two.

## Steps to Reproduce

1. Append a well-formed - [ ] **AC6** block with a Verify line under ## Impact of any bug. 2. `verify_ac.py` run --id <bug> --dir sdlc-studio/bugs prints ac=6. 3. critic.py brief --unit <bug> --seat product renders AC1 to AC5. 4. validate.py check and gate.py pass.

## Proposed Fix

One reader: `parse_story` and the brief renderer read the criteria through `sdlc_md.criteria_section`, and validate refuses an ACn block that sits outside the Acceptance Criteria section, naming the heading it was found under. Pin with a fixture carrying a criterion under Impact and assert every consumer agrees on the count.

## Acceptance Criteria

- [ ] **AC1** Given a bug or story whose `**ACn**` block sits under a heading other than `## Acceptance Criteria` (the fixture appends one under `## Impact`), when `validate.py check` runs, then it reports an ERROR naming the artefact, the criterion id and the heading it sits under, and an artefact whose criteria all sit in their section reports none - the control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::BugCriteriaTests::test_a_criterion_outside_its_section_is_an_error_naming_the_heading
- [ ] **AC2** Given the same artefact, when `verify_ac.py run` and `critic.py brief` read it, then both report the same criterion count, the count of the section's criteria, and the misplaced block is neither executed nor briefed - today `verify_ac` executes it and the brief omits it, so a verifier passes that no reviewer ever judged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::CriteriaSectionTests::test_verify_ac_and_the_brief_count_the_same_criteria
- [ ] **AC3** Given the same artefact, when `verify_ac.py lint --bugs` runs, then the misplaced criterion is named as unreviewable with the section it belongs in, so the author is told where to move it rather than left with a green run and a silent brief
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::CriteriaSectionTests::test_lint_names_a_misplaced_criterion_with_its_section

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `validate.py`, report the misplaced block as a WARNING instead of an ERROR | Given a bug or story whose `**ACn**` block sits under a heading other than `## Acceptance Criteria` (the fixture appends one under `## Impact`), when `validate.py check` runs, then it reports an ERROR naming the artefact, the criterion id and the heading it sits under, and an artefact whose criteria all sit in their section reports none - the control |
| AC1 | in `validate.py`, name the artefact and the id but not the heading | Given a bug or story whose `**ACn**` block sits under a heading other than `## Acceptance Criteria` (the fixture appends one under `## Impact`), when `validate.py check` runs, then it reports an ERROR naming the artefact, the criterion id and the heading it sits under, and an artefact whose criteria all sit in their section reports none - the control |
| AC2 | in `verify_ac.py`, keep executing every `**ACn**` block wherever it sits - today's code | Given the same artefact, when `verify_ac.py run` and `critic.py brief` read it, then both report the same criterion count, the count of the section's criteria, and the misplaced block is neither executed nor briefed - today `verify_ac` executes it and the brief omits it, so a verifier passes that no reviewer ever judged |
| AC2 | in `critic.py` `brief`, read every `**ACn**` block in the file so the brief agrees with today's verify_ac by widening rather than narrowing | Given the same artefact, when `verify_ac.py run` and `critic.py brief` read it, then both report the same criterion count, the count of the section's criteria, and the misplaced block is neither executed nor briefed - today `verify_ac` executes it and the brief omits it, so a verifier passes that no reviewer ever judged |
| AC3 | in `verify_ac.py` `lint`, skip blocks outside the section silently | Given the same artefact, when `verify_ac.py lint --bugs` runs, then the misplaced criterion is named as unreviewable with the section it belongs in, so the author is told where to move it rather than left with a green run and a silent brief |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
