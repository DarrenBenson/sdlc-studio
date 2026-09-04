# BG0648: a criterion written outside the Acceptance Criteria section is executed by verify_ac and invisible to the brief, the transition gate, validate and the sprint report

> **Status:** Open
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

- [ ] **AC1** Given an artefact with an ACn block under a heading other than Acceptance Criteria, when validate.py check runs, then it refuses naming the block and the heading
  - **Verify:** manual - the executable verifier is authored when this is groomed
- [ ] **AC2** Given the same artefact, when `verify_ac` run and critic.py brief read it, then both report the same criterion count
  - **Verify:** manual - the executable verifier is authored when this is groomed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
