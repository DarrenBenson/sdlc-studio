# BG1634: Three reference pages still say the scripts fall back to defaults without PyYAML

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-upgrade.md, .claude/skills/sdlc-studio/reference-scripts-domain.md, tools/tests/test_config_refusal_pages.py, changelog.d/BG1634.md
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T23:29:10Z

## Summary

US1297 made every config-reading command refuse when PyYAML will not import (exit 1, one stderr line). Three shipped reference pages still describe the removed behaviour: reference-config.md:112-115 says config.get degrades to the built-in default, reference-upgrade.md:104-106 says migrate on a machine without PyYAML writes nothing and reports the keys, and reference-scripts-domain.md:385 calls config.py degrading without PyYAML. A consuming agent reading them expects a run to continue on defaults and will misread the refusal. Found by US1297's qa review (verdict bcfc37ba3088-151ac7b1, non-blocking, RUN-01M7TTK3).

## Steps to Reproduce

Hide PyYAML (PYTHONPATH to a dir with a yaml.py that raises ImportError) and run status.py hint in a project with a .config.yaml: it exits 1 with one stderr line. Then read reference-config.md:112-115, reference-upgrade.md:104-106 and reference-scripts-domain.md:385: each says the run continues on defaults.

## Proposed Fix

Reword the three passages to say a config-reading command refuses (exit 1, one line naming PyYAML) when PyYAML will not import, and add a test that fails if any of the three pages says degrade, fall back or default without PyYAML.

## Acceptance Criteria

- [ ] **AC1** Given `reference-config.md`, `reference-upgrade.md` and `reference-scripts-domain.md`, when every paragraph that names PyYAML is read, then each says a config-reading command refuses (exit 1) when PyYAML will not import, and no such paragraph says the scripts degrade, fall back, or carry on with the built-in defaults.
  - **Verify:** pytest tools/tests/test_config_refusal_pages.py::ReferencePagesPyYamlTests::test_every_pyyaml_paragraph_says_the_command_refuses
  - **Verified:** yes (2026-11-20)
- [ ] **AC2** Fails on: restoring any one of the three removed passages (`config.get` degrades to the built-in default; migrate without PyYAML writes nothing and reports the keys; config.py degrading without PyYAML) fails the AC1 test, each judged by paragraph rather than by a fixed phrase list.
  - **Verify:** pytest tools/tests/test_config_refusal_pages.py::ReferencePagesPyYamlTests::test_a_restored_fallback_passage_fails_the_check
  - **Verified:** yes (2026-11-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-23 | sdlc-studio | Renamed the tools-side page check to tools/tests/test_config_refusal_pages.py in Affects and both Verify lines, so unittest discovery over tools/tests no longer clashes with the skill test module of the old name (BG1730) |
