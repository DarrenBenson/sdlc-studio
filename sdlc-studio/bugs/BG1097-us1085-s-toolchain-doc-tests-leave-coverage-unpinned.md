# BG1097: US1085's toolchain-doc tests leave coverage unpinned, still pass three counted phrasings, and fail at collection without PyYAML

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_gate_toolchain_docs.py, changelog.d/BG1097.md
> **Evidence:** US1085 QA review, round 2 (APPROVE), qa-seat-US1085-r1, 2026-10-19, at 7916edc3: [new] items 1, 3 and 4.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T20:49:04Z

## Summary

`_soft_dependencies` reads only guarded imports, so the coverage clause (reached through a subprocess) can be deleted from the TRD with the suite green. The count check is still a list of banned phrasings: 'chains all ten', 'a ten-check chain' and 'ten markdown lint checkers' pass. And `import yaml` is unconditional, so without PyYAML all five tests fail at collection (sibling guards do the same).

## Steps to Reproduce

Delete the TRD's coverage clause, or add 'a ten-check chain' to the TSD, and run tools/tests/`test_lean_gate_toolchain_docs.py`: green.

## Proposed Fix

Pin coverage from `verify_ac`'s own absent-module message, judge a count by any number word beside the lint chain's name, and import yaml inside the one test that reads YAML.

## Acceptance Criteria

- [ ] **AC1** Given coverage deleted from the TRD's soft-dependency row, when the toolchain-doc tests run, then they fail: the soft dependencies the test derives include each third-party module a shipped script imports in a `python -c` subprocess probe (coverage, from verify_ac.py's coverage_version), not only its guarded imports
  - **Verify:** pytest tools/tests/test_lean_gate_toolchain_docs.py::GateToolchainDocsTests::test_a_subprocess_probed_soft_dependency_is_named

## Impact

A later edit can drop a true claim or restore a count with the document tests green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
