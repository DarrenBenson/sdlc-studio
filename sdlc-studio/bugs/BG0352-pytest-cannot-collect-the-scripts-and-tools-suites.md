# BG0352: pytest cannot collect the scripts and tools suites in one invocation, so no Verify line can span both

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests, tools/tests, pytest.ini
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

Four lanes hit this independently. `scripts/tests` and `tools/tests` are both named `tests`, so pytest's package resolution refuses node ids from both in one command. A Verify line therefore cannot name tests in both halves of the gate, and a unit whose change spans them has no single executable proof.

## Steps to Reproduce

`python3 -m pytest tools/tests/test_help_coverage.py .claude/skills/sdlc-studio/scripts/tests/test_gate.py -q` -> `ModuleNotFoundError: No module named 'tests.test_gate'` / `Interrupted: 1 error during collection`. Each ; `python3 -m pytest "tools/tests/test_doc_claims.py::RepairCoverageTests::test_an_unpinned_repair_is_reported" ".claude/skills/sdlc-studio/scripts/tests/test_mutation.py::IsolationTests::test_mutation_refuses_a_dirty_file; cd /home/darren/code/DarrenBenson/sdlc-studio && python3 -m pytest .claude/skills/sdlc-studio/scripts/tests tools/tests -q --junit-xml=/tmp/full.xml
-> ImportError while importing test module 'tools/tests/test_audit_quiz; $ python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::IterTablesFenceTests tools/tests/test_check_links.py::NestedFenceTests -q
ERROR: found no collectors for /home/darren/code/DarrenBenson/sdlc-s;`python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/`test_shell_hazard_rate.py` tools/tests/`test_check_neutrality.py` tools/tests/`test_lint_style.py` -q` gives `ModuleNotFoundError: No module named '`tests.test_lint_s`

## Proposed Fix

See the summary; each cited site names its own remedy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
