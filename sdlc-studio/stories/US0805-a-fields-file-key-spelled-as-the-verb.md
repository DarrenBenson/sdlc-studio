# US0805: A `--fields-file` key spelled as the verb's own flag (`ac`, `option`, `type`, `status`) is accepted as its canonical field

> **Status:** Ready
> **Delivers:** CR0559
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_fields_file_flag_keys.py, changelog.d/US0805.md
> **Epic:** EP0244
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a `--fields-file` document to accept a key spelled exactly as the flag I would otherwise pass (`ac` for `--ac`, `option` for `--option`, `type` for `--type`, `status` for `--status`)
**So that** moving an invocation from flags into a document does not cost a refusal and a retry

## Summary

Groomed under D0291 (sdlc-studio/reviews/backlog-sweep-2026-10-01.md), 2 points. `file_finding.load_fields_file` refuses any key outside the canonical set, and the canonical set spells list fields in the plural (`acs`, `options`), so the flag's own spelling is refused as unknown. `decisions.py add` reads only `decision` and `rationale` from the document, so `status` and `supersedes`, both flags of the same verb, are refused. `file_finding.py file` requires `--type` on the command line and refuses a `type` key in the document. This absorbs the second half of CR0592 bullet 58 ("`--fields-file` refuses a 'type' key while `--type` is required"); its first half (an `acs` list of objects written as a Python repr) is a different defect and stays in CR0592.

The flag spelling maps to the canonical field in one place, `load_fields_file`, so `artifact.py new` inherits it. A document carrying both spellings of one field stays refused by the existing unknown-key path, as at HEAD: no new refusal. An explicit flag still overrides the document.

## Premise at HEAD

Executed at `85042135` against a scratch fixture:

```text
$ file_finding.py file --type bug --fields-file ff.json --dry-run   # ff.json carries "ac": [...]
file refused: --fields-file ff.json carries unknown field(s): ac - known fields are title, summary, ... acs, options, ...
exit=1
$ decisions.py add --fields-file d.json                             # d.json carries "status": "accepted"
error: --fields-file d.json carries unknown field(s): status - known fields are decision, rationale.
exit=2
$ file_finding.py file --fields-file t.json --dry-run               # t.json carries "type": "bug"
file_finding.py file: error: the following arguments are required: --type
exit=2
```

## Acceptance Criteria

- [ ] **AC1** Given a fixture and a document carrying `ac` and `option` lists, when `file_finding.py file --type bug --fields-file <doc> --dry-run --root <fixture>` runs, then it exits 0 and the previewed bug carries those criteria exactly as an `acs` document would. Fails on: HEAD exits 1 `carries unknown field(s): ac`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fields_file_flag_keys.py::FieldsFileFlagKeysTests::test_ac_and_option_map_to_acs_and_options
- [ ] **AC2** Given a fixture and a document carrying `decision`, `rationale` and `"status": "revisited"`, when `decisions.py add --fields-file <doc> --root <fixture>` runs, then it exits 0 and the recorded row's status is `revisited`. Fails on: HEAD exits 2 `carries unknown field(s): status`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fields_file_flag_keys.py::FieldsFileFlagKeysTests::test_decisions_add_reads_status_from_the_document
- [ ] **AC3** Given a fixture and a document carrying `"type": "bug"` with no `--type` flag, when `file_finding.py file --fields-file <doc> --dry-run --root <fixture>` runs, then it exits 0 and previews a bug; with neither a `type` key nor `--type` it still exits 2 naming `--type`. Fails on: HEAD exits 2 `the following arguments are required: --type`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fields_file_flag_keys.py::FieldsFileFlagKeysTests::test_a_type_key_stands_in_for_the_type_flag
- [ ] **AC4** Given a fixture and a document carrying `seat`, `subject`, `question`, `ruling` and `reason`, when `decisions.py rule --fields-file <doc> --root <fixture>` runs with no `--seat` or `--subject` flag, then the ruling is recorded under that seat and subject. Fails on: the current code, which refuses `seat` and `subject` as unknown fields and then demands both flags (found in the 2026-10-01 backlog sweep)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_fields_file_flag_keys.py::FieldsFileFlagKeysTests::test_decisions_rule_reads_seat_and_subject_from_the_document

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | backlog sweep 2026-09-15 | Backlog sweep 2026-09-15: a further instance - decisions.py add --fields-file refuses a 'status' key ('carries unknown field') although --status is a flag of the same verb, so CR0417's own AC1 never reached decisions.py. Hit while recording D0187-D0192. |
| 2026-10-01 | sdlc-studio | Retitled: was "A `--fields-file` document whose keys are spelled as the verb's own flags is accepted" |
| 2026-10-01 | engineering seat (groomer) | Groomed under D0291 (backlog sweep 2026-10-01): criteria authored, premise executed at HEAD 85042135, Points and Affects set |
| 2026-10-01 | backlog sweep | AC4 added: `decisions.py rule` reads seat and subject from a fields file (hit during the sweep); points 2 to 3. |
