# BG0624: a finding at a severity in neither the barred nor the disclosed set is silently absent from BOTH the release bar and the disclosure page

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** tools/known_issues.py, tools/tests/test_known_issues.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** Adversarial review of BG0621, wave 1 of RUN-01M0YXN3, 2026-08-26. Severity census over the corpus: 299 Medium, 221 High, 74 Low, 10 medium, 7 high, 7 Critical, 4 low, 1 major. Origin dated to the base ref by inspection - `corpus` and `barred_open` both filtered on set membership before BG0621 and still do.
> **Verification depth:** functional [[derived: criteria 5; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 3 of 5 criteria through the shipped CLI, 2 in-process | fp 740a30615346 ]] (five criteria, every mutant applied to the real file with bytecode purged and the tree restored. Three reach the shipped commands - `--bar` and both writers - and AC5's discriminator is the EXIT CODE as well as the text, because under a widen-the-bar mutant the id also appears, in the not-met line, and only the exit separates them. AC3 and AC4 each name a positive control in their own test rather than inheriting one by accident from a neighbouring suite: a guard comparing against the wrong set, or case-sensitively, refuses a recognised severity as well as an unrecognised one.)
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

## Two decisions this fix must make

**Which population the residue covers.** The sole unrecognised value in the corpus today is
BG0149's `major`, and BG0149 is at Fixed - and both readers test open-ness BEFORE severity,
so it is excluded twice over. Cover every finding file and the lane nags about a closed bug
for ever; cover only open ones and the sole real instance stays invisible. This fix covers
EVERY finding file, and the residue is reported rather than blocking, so a closed unit is
named once and can be corrected rather than nagged about.

**Whether an unclassifiable severity holds the bar.** It does NOT block. `--bar` already
refuses on an unreadable finding, so a precedent exists for blocking - but an unreadable
finding cannot be judged at all, while an unrecognised severity can be read and corrected in
one edit. Naming it on both surfaces is what the bug asks for; refusing on it would make the
release bar hostage to a typo.

**The class is not closed by this unit.** `artifact.py new --type bug|issue` is a SECOND
writer of the same free-string field, so normalising in the filer alone leaves the class open
through the other door. Both writers are in scope here; nothing else writes it.

## Acceptance Criteria

- [ ] **AC1** Given a finding whose Severity matches neither the barred nor the disclosed set, when the residue is read, then it is NAMED in the residue report AND is absent from `corpus()`'s mapping. Both halves: "reported rather than absent" is satisfied by the id merely appearing in output, and under the classify-as-disclosed mutant it does appear - on the page, as a disclosed finding
  - **Verify:** pytest tools/tests/test_known_issues.py::UnclassifiableSeverityTests::test_an_unrecognised_severity_is_named_and_not_silently_disclosed
  - **Verified:** yes (2026-08-28)
- [ ] **AC2** Given a MEDIUM finding, when the population is read, then it is disclosed and NOT barred; and given a HIGH one, barred and not disclosed. The control names BOTH directions, because a mutant folding one reader into the other moves a recognised severity and an assertion about one side alone survives it
  - **Verify:** pytest tools/tests/test_known_issues.py::UnclassifiableSeverityTests::test_a_recognised_severity_is_classified_exactly_as_today
  - **Verified:** yes (2026-08-28)
- [ ] **AC3** Given an unrecognised severity offered to `file_finding.py`, when the finding is filed, then it is REFUSED naming the accepted set - not normalised, which would guess at intent. The criterion and its selector state one behaviour between them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::SeverityVocabularyTests::test_an_unrecognised_severity_is_refused_at_filing
  - **Verified:** yes (2026-08-28)
- [ ] **AC4** Given the SECOND writer, `artifact.py new --type bug`, when an unrecognised severity is offered, then it is refused the same way. Normalising one entry point leaves the class open through the other, so stopping the class is a claim only both together can make
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::SeverityVocabularyTests::test_the_creator_refuses_an_unrecognised_severity_too
  - **Verified:** yes (2026-08-28)
- [ ] **AC5** Given the shipped commands, when `known_issues.py --bar` and `--check` are run as SUBPROCESSES over a fixture holding an unrecognised severity, then both NAME it and `--bar` still exits 0, because an unclassifiable severity is reported rather than barring. The Impact is stated entirely in terms of these two commands, and a repair widening the population functions while `--bar` prints `release bar met` passes every library row
  - **Verify:** pytest tools/tests/test_known_issues.py::UnclassifiableSeverityTests::test_both_commands_name_an_unclassifiable_severity
  - **Verified:** yes (2026-08-28)

## Impact

The release bar and the disclosure page are the two surfaces a release is judged on, and a finding can be absent from both because somebody typed a word neither list expects. The current instance is harmless only by luck of being Fixed - the same typo on an open finding would hide it from the bar completely, which is the exact defect BG0621 was filed for.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/known_issues.py`, classify an unrecognised severity into the DISCLOSED set rather than naming it as residue, so it silently joins the page instead of being reported - the tidier-looking repair, and the one an id-appears-somewhere oracle cannot catch | Given a finding whose Severity matches neither the barred nor the disclosed set, when the residue is read, then it is NAMED in the residue report AND is absent from `corpus()`'s mapping. Both halves: "reported rather than absent" is satisfied by the id merely appearing in output, and under the classify-as-disclosed mutant it does appear - on the page, as a disclosed finding |
| AC2 | in `tools/known_issues.py`, replace `barred_open`'s own read with a filter over `corpus()` - the over-correction its docstring names as the reason the two reads are kept separate - so a recognised severity is classified by one predicate instead of two | Given a MEDIUM finding, when the population is read, then it is disclosed and NOT barred; and given a HIGH one, barred and not disclosed. The control names BOTH directions, because a mutant folding one reader into the other moves a recognised severity and an assertion about one side alone survives it |
| AC3 | in `.claude/skills/sdlc-studio/scripts/file_finding.py`, revert `--severity` to a free string by removing its vocabulary check, so an unrecognised value reaches the artefact and the residue report becomes the only line of defence | Given an unrecognised severity offered to `file_finding.py`, when the finding is filed, then it is REFUSED naming the accepted set - not normalised, which would guess at intent. The criterion and its selector state one behaviour between them |
| AC4 | in `.claude/skills/sdlc-studio/scripts/artifact.py`, remove the vocabulary check from `artifact.py new`, leaving it only in `file_finding.py`, so the field is written verbatim through the second writer and the class stays open | Given the SECOND writer, `artifact.py new --type bug`, when an unrecognised severity is offered, then it is refused the same way. Normalising one entry point leaves the class open through the other, so stopping the class is a claim only both together can make |
| AC5 | in `tools/known_issues.py`, remove the residue line from what `--bar` and `--check` PRINT while leaving both library readers correct, so neither command reports what it computed | Given the shipped commands, when `known_issues.py --bar` and `--check` are run as SUBPROCESSES over a fixture holding an unrecognised severity, then both NAME it and `--bar` still exits 0, because an unclassifiable severity is reported rather than barring. The Impact is stated entirely in terms of these two commands, and a repair widening the population functions while `--bar` prints `release bar met` passes every library row |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
