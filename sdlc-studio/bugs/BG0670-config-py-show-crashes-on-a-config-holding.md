# BG0670: config.py show crashes on a config holding an unquoted YAML date, so the catalogued verb cannot print this repository's own configuration

> **Status:** In Progress
> **Verification depth:** functional [[derived: criteria 3; plan rows 3; executed 3; killed 3; survived 0; lines ruled 1; not-run 0; entry point 2 of 3 criteria through the shipped CLI, 0 in-process; 1 undetermined (the named node could not be isolated) | fp d080cd22047c ]]
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`config.py show` (no --key) prints `json.dumps(load_config())`. PyYAML loads an unquoted YAML date as `datetime.date`, and json.dumps raises a `TypeError` that an object of type `date` cannot be turned into JSON - exit 1. This repository's own `.config.yaml` carries unquoted dates under `gate_budget` (`baseline_date` and two more), so the verb crashes here, and on any consuming project that writes a date the natural way. The verb is catalogued in reference-scripts-surface.md. Reproduced at 51f264db; found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. From the repository root run `python3 .claude/skills/sdlc-studio/scripts/config.py show`.
2. Observe exit 1 and a `TypeError` naming the `date` object and dict item `'gate_budget'` (CPython's json message, whose spelling the house style does not quote).

## Proposed Fix

Serialise with a default that renders date and datetime values as ISO-8601 strings, so the printed configuration is the one that was written. Keep `--key` behaviour unchanged.

## Acceptance Criteria

- [ ] **AC1** `config.py show` on a config holding an unquoted YAML date NESTED under a key (as `gate_budget.baseline_date` is here) prints the merged configuration and exits 0, the date rendered as ISO-8601
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ShowSerialisesDatesTests::test_an_unquoted_date_prints_as_iso
  - **Verified:** yes (2026-09-15)
- [ ] **AC2** The printed configuration is valid JSON
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ShowSerialisesDatesTests::test_the_output_is_valid_json
  - **Verified:** yes (2026-09-15)
- [ ] **AC3** `config.py show` on this repository's own configuration exits 0 - the real-target control
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/config.py show > /dev/null
  - **Verified:** yes (2026-09-15)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/config.py, pass default=repr to the json.dumps call in cmd_show, so the date prints as the string datetime.date(2026, 7, 26) rather than 2026-07-26 | `config.py show` on a config holding an unquoted YAML date NESTED under a key (as `gate_budget.baseline_date` is here) prints the merged configuration and exits 0, the date rendered as ISO-8601 |
| AC2 | in .claude/skills/sdlc-studio/scripts/config.py, replace json.dumps in cmd_show with yaml.safe_dump of load_config, which exits 0 and keeps the date ISO but prints YAML | The printed configuration is valid JSON |
| AC3 | in .claude/skills/sdlc-studio/scripts/config.py, replace date values with ISO strings only at the top level of the dict cmd_show serialises, without recursing, so the nested gate_budget.baseline_date still reaches json.dumps as a date | `config.py show` on this repository's own configuration exits 0 - the real-target control |

## Coverage Rulings

| File | Line | Hash | Reason | Author | Date |
| --- | --- | --- | --- | --- | --- |
| .claude/skills/sdlc-studio/scripts/config.py | 134 | bd9ddac54bf04bc3 | the fallback keeps json.dumps's own refusal for any value that is not a date or datetime; yaml.safe_load yields only JSON types plus date/datetime (and bytes via an explicit !!binary tag, outside this bug), so no criterion's fixture can reach it without asserting a crash no criterion asks for | sdlc-studio | 2026-09-15 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
