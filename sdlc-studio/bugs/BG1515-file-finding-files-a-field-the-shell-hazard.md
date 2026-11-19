# BG1515: file_finding files a field the shell-hazard sweep refuses, so the refusal arrives at the push gate's full suite instead of at filing

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1515.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T20:30:46Z

## Summary

BG1507's Steps carried a `$(` command substitution and BG1514's Summary a quoted assertion with a space before a colon. `file_finding.py` filed both from a --fields-file, the commit's selected lanes passed them, and the push gate's full suite refused main on `test_shell_hazard_rate`'s legitimate-field sweep, 14 minutes later.

## Steps to Reproduce

1. File a bug whose steps field holds a dollar sign and an opening parenthesis, with --fields-file.
2. Commit it: the commit passes.
3. Push: the push gate's full suite reds `test_shell_hazard_rate.`

## Proposed Fix

Run the same shell-hazard detector over each field at filing and refuse, naming the field and the hazard, as the sweep would.

## Acceptance Criteria

- [ ] **AC1** Given a fields file whose steps field holds a dollar sign followed by an opening parenthesis, when `file_finding.py file` reads it, then filing is refused naming the field and the hazard as the sweep in `test_shell_hazard_rate.py` would, no artefact is written and no id is allocated. Fails on: a finding filed that the push gate's full suite then refuses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FilingRefusesShellHazardTests::test_a_hazardous_field_in_a_fields_file_is_refused_and_nothing_is_written
- [ ] **AC2** Given the same text inside a fenced code block, or in a field that carries the quotes-shell-hazard marker, when it is filed, then the finding is filed and the field lands byte for byte. Fails on: a filer that refuses a hazard the sweep exempts.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FilingRefusesShellHazardTests::test_a_field_the_sweep_exempts_is_filed
- [ ] **AC3** Given each field the sweep judges (`HAZARD_FIELDS`) and each hazard its detector names, when a finding carrying one is filed by flag or by fields file, then filing refuses it through the same `shell_hazards` detector the sweep calls. Fails on: a second detector at filing that drifts from the sweep, or a field or input path the filer leaves unchecked.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FilingRefusesShellHazardTests::test_filing_and_the_sweep_refuse_the_same_fields_and_hazards

## Impact

One push-gate cycle per hazardous phrase in a filed finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
