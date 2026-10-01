# US0970: The finding writers keep every criterion and verifier they were given

> **Status:** Ready
> **Delivers:** CR0592
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_finding_writer_keeps_input.py, changelog.d/US0970.md
> **Epic:** EP0270
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the finding writers to store every criterion and verifier I hand them, in the shape I wrote
**So that** a filed artefact never silently loses a Verify line or turns a criterion into Python repr text

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md) from CR0592 bullets 32, 46 and the first half of 58 (its `type`-key half is US0805), 3 points.

- #32 `file_finding.py file --type cr` and `artifact.py new --type cr` accept `acs` plus `verify` and write the criteria with no Verify lines at exit 0. An extra, unpaired or blank verifier is mis-paired at exit 0; reporting it removes a false success.
- #58 an `acs` list of objects (`{"id", "text", "verify"}`) is written as the object's Python repr with no Verify line.
- #46 `check_verify_selectors` refuses a new test whose name extends an existing method in the named class (`test_x` exists, `test_x_in_slug_form` is new) as a typo. This loosens a false refusal; a true near-miss typo is still refused, as today.

## Premise at HEAD

Executed at `85042135` in a scratch project after `init.py run`, with `acs: [{"id": "AC1", "text": "Given x then y", "verify": "pytest t.py::A::test_b"}]`:

```text
$ python3 file_finding.py file --type bug --fields-file o.json --root .
warning: 1 authored criterion/criteria carry no verifier (AC1) ...
filed BG-01M3VAF0 -> .../BG-01M3VAF0-probe-obj-acs.md
exit=0
$ grep AC1 sdlc-studio/bugs/BG-01M3VAF0-probe-obj-acs.md
- [ ] **AC1** {'id': 'AC1', 'text': 'Given x then y', 'verify': 'pytest t.py::A::`test_b`'}
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture, when `file_finding.py file --type cr --fields-file <doc>` runs with two `acs` and two `verify` entries, and when `artifact.py new --type cr --ac a --verify <s1> --ac b --verify <s2>` runs, then each CR carries both Verify lines, each under its own criterion. Fails on: HEAD writes both criteria with no Verify line at exit 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_finding_writer_keeps_input.py::FindingWriterKeepsInputTests::test_a_cr_keeps_its_verify_lines
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given `verify` with one more entry than `acs`, or a blank `verify` entry, when either writer runs, then it exits non-zero naming the unpaired or blank verifier and writes nothing. Fails on: HEAD mis-pairs it and exits 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_finding_writer_keeps_input.py::FindingWriterKeepsInputTests::test_an_unpaired_verifier_is_named_not_mis_paired
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given a document whose `acs` list holds `{"id": "AC1", "text": "Given x then y", "verify": "pytest t.py::A::test_b"}`, when `file_finding.py file --type bug --fields-file <doc>` runs, then AC1 reads `Given x then y` and carries `Verify: pytest t.py::A::test_b`. Fails on: HEAD writes the object's repr as the criterion text (premise)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_finding_writer_keeps_input.py::FindingWriterKeepsInputTests::test_criterion_objects_are_read_as_text_and_verify
  - **Verified:** yes (2026-10-01)
- [ ] **AC4** Given a test class holding `test_x`, when `file_finding.py file` names `ThatClass::test_x_in_slug_form` as a Verify selector, then it files the finding as a not-yet-written test; a one-letter typo of `test_x` in the same class is still refused with `did you mean`. Fails on: HEAD refuses `AmigoNameTests::test_no_amigo_passage_names_a_retired_seat_in_slug_form` as a near miss
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_finding_writer_keeps_input.py::FindingWriterKeepsInputTests::test_an_extended_test_name_files_as_new
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
