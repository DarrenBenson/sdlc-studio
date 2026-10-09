# BG1013: The waiver remedy the close and the checklist print omits --authorised-by, so the command as printed is refused

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_waiver_remedy_runs.py, changelog.d/BG1013.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** decisions.py waive refusal text, reproduced; the three remedy sites named.
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T09:03:07Z

## Summary

Three remedies print `decisions.py waive --subject rule:sprint-checklist:<item> --rationale '<why>'` (sprint.py:5661, sprint.py:7202, `sprint_report.py`:2428), but `decisions.py waive` refuses a checklist waiver without `--authorised-by`: 'waive refused: a waiver of rule:sprint-checklist:closing-review must record WHO authorised it'. Reproduced at d327d5d0 by running the printed command. Found by the G5 panel review (D0355).

## Steps to Reproduce

Run the remedy exactly as a close prints it -> refused.

## Proposed Fix

Print `--authorised-by "<the operator>"` in all three remedies, from one shared constant so they cannot drift again.

## Acceptance Criteria

- [ ] **AC1** Every waiver remedy the close or the checklist prints, run as printed with its placeholders filled, records the waiver
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_waiver_remedy_runs.py::WaiverRemedyTests::test_each_printed_remedy_records_as_printed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Filed |
