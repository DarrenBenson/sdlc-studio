# BG1506: US0996's AC3 test fails whenever test_sprint_report's CloseReportTests ran first in the same pytest process, so the release gate and CI's corpus check read it red

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T16:05:58Z

## Summary

gate.py --release on devserver1 refused cd0e478e on one red criterion, US0996::AC3, and CI's scheduled corpus check on e356db80 named the same one; the test passes alone and in a clean clone. `CloseReportTests._mod` in `test_sprint_report.py` execs a fresh `sprint_report` into sys.modules['`sprint_report`'] and never restores the module it replaced. `test_evidence_schema_stamp.py` patches the `sprint_report` it imported at load time, while the close it drives (`annex._close`, through `annex._live)` reads sys.modules NOW, so once the module has been swapped the unstamped writer's patch misses, the earlier page is stamped, and the test fails on '`evidence_schema` unexpectedly found'. The release gate batches every pytest verifier in one session across xdist workers, so which worker holds both files decides the verdict: run fifteen's new test modules moved the split.

## Steps to Reproduce

1. In a clone at cd0e478e: python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/`test_sprint_report.py` .claude/skills/sdlc-studio/scripts/tests/`test_evidence_schema_stamp.py`
2. `test_an_unstamped_page_still_checks_valid` fails: `evidence_schema` unexpectedly found in the before page.
3. python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/`test_evidence_schema_stamp.py` alone passes.

## Proposed Fix

`CloseReportTests._mod` restores whatever sys.modules held for `sprint_report` when the test ends, and `test_evidence_schema_stamp` patches the live module (`annex._live(`'`sprint_report`')) for the unstamped writer and the `at_close` and `at_sign` patches, as its own docstring says the close reads it.

## Acceptance Criteria

- [ ] **AC1** Given a fresh sprint_report put in sys.modules after the stamp tests were imported, as CloseReportTests did, when the four EvidenceSchemaStampTests run, then all four pass; and with CloseReportTests collected before them in one pytest process they pass too. Fails on: the stamp tests patching the module they imported at load rather than the live one.
  - **Verify:** shell python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::CloseReportTests .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py && python3 -c "import sys,unittest,importlib.util; sys.path[:0]=['.claude/skills/sdlc-studio/scripts','.claude/skills/sdlc-studio/scripts/tests']; import test_evidence_schema_stamp as t; s=importlib.util.spec_from_file_location('sprint_report','.claude/skills/sdlc-studio/scripts/sprint_report.py'); m=importlib.util.module_from_spec(s); sys.modules['sprint_report']=m; s.loader.exec_module(m); r=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromModule(t)); sys.exit(0 if r.wasSuccessful() and r.testsRun==4 else 1)"
  - **Verified:** yes (2026-11-16)
- [ ] **AC2** Given CloseReportTests has run, then sys.modules['`sprint_report`'] is the module it held before the class ran, and the stamp tests still pass alone. Fails on: a `_mod` that leaves its fresh module in sys.modules.
  - **Verify:** shell python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_evidence_schema_stamp.py && python3 -c "import sys,unittest; sys.path[:0]=['.claude/skills/sdlc-studio/scripts','.claude/skills/sdlc-studio/scripts/tests']; import sprint_report as before; import test_sprint_report as t; r=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(t.CloseReportTests)); sys.exit(0 if r.wasSuccessful() and sys.modules['sprint_report'] is before else 1)"
  - **Verified:** yes (2026-11-16)

## Impact

The v6.4.0 release gate cannot pass, and main's scheduled corpus check is red, though no shipped behaviour is wrong.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
