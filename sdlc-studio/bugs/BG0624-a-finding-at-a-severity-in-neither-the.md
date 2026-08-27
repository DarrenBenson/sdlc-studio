# BG0624: a finding at a severity in neither the barred nor the disclosed set is silently absent from BOTH the release bar and the disclosure page

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Adversarial review of BG0621, wave 1 of RUN-01M0YXN3, 2026-08-26. Severity census over the corpus: 299 Medium, 221 High, 74 Low, 10 medium, 7 high, 7 Critical, 4 low, 1 major. Origin dated to the base ref by inspection - `corpus` and `barred_open` both filtered on set membership before BG0621 and still do.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`BARRED` is Critical and High; `DISCLOSED` is Medium and Low. A finding whose Severity is neither matches no set, so `barred_open` skips it and `corpus` skips it, and it appears on neither surface a release is judged on - with nothing said. The live instance is BG0149 at `Severity: major`, found by the BG0621 review on 2026-08-26. It is Fixed today so nothing is currently hidden, and the defect is present at the base ref rather than introduced by BG0621. This is the FOURTH shape of the same failure BG0621 repaired three of: the readers enumerate what they recognise and drop what they do not, and a finding dropped is indistinguishable from a corpus with nothing in it. BG0621's `unparseable` guard does not catch it, because the file PARSES - every field is present and well-formed. It is the value that is unrecognised.

## Steps to Reproduce

1. File a bug with `> **Severity:** major`, or any value outside Critical, High, Medium and Low. 2. `python3 tools/known_issues.py --bar` reports the bar met. 3. `--check` shows the page agrees with the corpus. 4. `unparseable()` returns nothing, because the file is perfectly readable. The finding exists and neither surface mentions it.

## Proposed Fix

Classify against the union and REPORT the residue. A severity matching neither set should be named the way BG0621 made an unreadable finding named - the guard already exists and needs only its population widened. The deeper repair is upstream: `file_finding.py` accepts any string for Severity, so the corpus holds `major`, and 10 `medium`, 7 `high` and 4 `low` that BG0621's case-insensitive match now rescues. Normalising at the point of filing would stop the class rather than the instance.

## Acceptance Criteria

- [ ] **AC1** Given a finding whose Severity matches neither the barred nor the disclosed set, when the bar and the page are read, then it is REPORTED rather than absent from both
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_severity_in_neither_set_is_reported
- [ ] **AC2** Given a finding at a recognised severity, when the population is read, then it is classified exactly as today - the paired control
  - **Verify:** pytest tools/tests/test_known_issues.py::BarPopulationTests::test_a_recognised_severity_is_unchanged
- [ ] **AC3** Given the filer, when a finding is written with an unrecognised severity, then it is NORMALISED or refused at the point of filing - the corpus holds `major`, and stopping the class beats catching the instance
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::SeverityVocabularyTests::test_an_unrecognised_severity_is_refused_at_filing

## Impact

The release bar and the disclosure page are the two surfaces a release is judged on, and a finding can be absent from both because somebody typed a word neither list expects. The current instance is harmless only by luck of being Fixed - the same typo on an open finding would hide it from the bar completely, which is the exact defect BG0621 was filed for.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/known_issues.py`, classify an unrecognised severity into the DISCLOSED set rather than reporting it, so it silently joins the page instead of being named as unclassifiable - the tidier-looking repair, and the one that hides the population gap | Given a finding whose Severity matches neither the barred nor the disclosed set, when the bar and the page are read, then it is REPORTED rather than absent from both |
| AC2 | in `tools/known_issues.py`, widen the barred set to every severity that is not explicitly disclosed, so a Medium finding starts holding the release bar - the over-correction, which AC1 alone cannot catch | Given a finding at a recognised severity, when the population is read, then it is classified exactly as today - the paired control |
| AC3 | .claude/skills/sdlc-studio/scripts/file_finding.py: remove the severity normalisation from the filer, so an unrecognised value is written to the artefact and the reporting in AC1 becomes the only line of defence | Given the filer, when a finding is written with an unrecognised severity, then it is NORMALISED or refused at the point of filing - the corpus holds `major`, and stopping the class beats catching the instance |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
