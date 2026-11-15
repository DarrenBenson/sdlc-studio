# BG1468: Main is red: personas.memory.validity_days is documented but absent from config-defaults.yaml, and persona_memory.py has an unregistered or-empty guard

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_store.py, changelog.d/BG1468.md
> **Evidence:** Run thirteen mid-run full suite on devserver1 for a6c9a4c0: 2 failed, 7921 passed.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:32:02Z

## Summary

The full suite on the gate host at a6c9a4c0 (and again at 61be40f3) fails two boundary tests that the lands' selected tests did not run. (1) `test_config.py`::DocTests::`test_doc_defaults_match_yaml`: reference-config.md documents `personas.memory.validity_days` (added by US1058, 2766fda5), but templates/config-defaults.yaml has no such key. (2) `test_ledger.py`::FieldsFileTypeTests::`test_a_new_or_empty_guard_is_refused_by_the_repository_check`: `persona_memory.py`'s fields-file helper (near line 935, added in fb36836a) tests a key with `fields.get(k) or ""`, which the repository check refuses; it should use `file_finding.prose_value(fields`, key), which tests presence.

## Steps to Reproduce

Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_config.py`::DocTests::`test_doc_defaults_match_yaml` and .claude/skills/sdlc-studio/scripts/tests/`test_ledger.py`::FieldsFileTypeTests at HEAD: both fail.

## Proposed Fix

Add `personas.memory.validity_days: 90` under a personas.memory block in config-defaults.yaml, matching the documented default and the code's default, and replace the or-empty guard with `file_finding.prose_value.`

## Acceptance Criteria

- [ ] **AC1** Given HEAD, when `test_config.py`'s DocTests run, then `test_doc_defaults_match_yaml` passes, with `personas.memory.validity_days` and `personas.memory.inject_max` present in config-defaults.yaml at their documented defaults. Fails on: the key absent or with a different default.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py::DocTests::test_doc_defaults_match_yaml
- [ ] **AC2** Given HEAD, when `test_ledger.py`'s FieldsFileTypeTests run, then the or-empty guard check passes with `persona_memory.py` registering no new guard. Fails on: any or-empty guard on a fields-file value in `persona_memory.py.`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::FieldsFileTypeTests::test_a_new_or_empty_guard_is_refused_by_the_repository_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
