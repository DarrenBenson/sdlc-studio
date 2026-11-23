# BG1642: config.py show prints a RuntimeError traceback without PyYAML instead of the one-line refusal

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/tests/test_config.py, tools/tests/test_config_refusal_pages.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T00:40:07Z

## Summary

US1297 made every config-reading command refuse in one stderr line (PyYamlRequired, exit 1) when PyYAML will not import. config.py keeps its own `_yaml` helper (config.py:31), which raises RuntimeError('config loading needs PyYAML (pip install pyyaml)'), so 'config.py show' in a project with no .config.yaml and PyYAML hidden ends in a full traceback, exit 1. Reproduced 2026-11-20. Found by BG1634's qa review (verdict 165644a30b29-e9ece581, pre-existing to that unit). The same review found BG1634's reference-page check accepts a sentence that denies the refusal ('does not refuse') and its `_EXIT_1` and negation-adjacency rules are unpinned.

## Steps to Reproduce

In an empty directory, put a yaml.py that raises ImportError on PYTHONPATH and run python3 .claude/skills/sdlc-studio/scripts/config.py show: exit 1 with a traceback ending in RuntimeError: config loading needs PyYAML.

## Proposed Fix

Route config.py's `_yaml` through `sdlc_md.require_pyyaml` so show refuses in one line, pin it in `test_config.py` with stderr asserted to hold no 'Traceback', and make the reference-page check refuse a negated refusal with a test on the `_EXIT_1` and negation-adjacency rules.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1297 made every config-reading command refuse in one stderr line (PyYamlRequired, exit 1) when PyYAML will not import.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In an empty directory, put a yaml.py that raises ImportError on PYTHONPATH and run python3 .claude/skills/sdlc-studio/scripts/config.py show: exit 1 with a...
- [ ] **AC3** The proposed fix lands, pinned by a test: Route config.py's `_yaml` through `sdlc_md.require_pyyaml` so show refuses in one line, pin it in `test_config.py` with stderr asserted to hold no 'Traceback'...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-23 | sdlc-studio | Renamed the tools-side page check to tools/tests/test_config_refusal_pages.py in Affects, so unittest discovery over tools/tests no longer clashes with the skill test module of the old name (BG1730) |
