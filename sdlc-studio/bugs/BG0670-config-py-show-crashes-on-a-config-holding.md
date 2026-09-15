# BG0670: config.py show crashes on a config holding an unquoted YAML date, so the catalogued verb cannot print this repository's own configuration

> **Status:** Open
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

- [ ] **AC1** `config.py show` on a config holding an unquoted YAML date prints the merged configuration and exits 0, the date rendered as ISO-8601
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ShowSerialisesDatesTests::test_an_unquoted_date_prints_as_iso
- [ ] **AC2** The printed configuration is valid JSON
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::ShowSerialisesDatesTests::test_the_output_is_valid_json
- [ ] **AC3** `config.py show` on this repository's own configuration exits 0 - the real-target control
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/config.py show > /dev/null

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
