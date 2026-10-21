# BG1043: The prerequisite check and the gate read pytest-xdist two different ways

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/gate_prereqs.py, tools/gate_timing.py, tools/tests/test_gate_prereqs.py, tools/tests/test_push_first_estimate.py, changelog.d/BG1043.md
> **Evidence:** US1006 round-1 QA verdict (sdlc-studio/reviews/critic-verdicts.md), the xdist note: gate_timing.py reads by metadata, gate.py:894 by find_spec; reported not blocking, by the story's design note.
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T15:07:54Z

## Summary

tools/`gate_prereqs.py` reads pytest-xdist by its distribution metadata (importlib.metadata, by name), and the push cost line follows it so the two agree (US1006). gate.py decides whether the suite runs in parallel by `importlib.util.find_spec(`"xdist"). The two disagree on an interpreter carrying the metadata without an importable module (a broken or partial install), or the module without the metadata (a vendored copy): the preflight and the cost line then say parallel while the gate runs serially, or the reverse. US1006's own parallel fixture is such a case: a bare dist-info with no module.

## Steps to Reproduce

Put a `pytest_xdist`-3.6.0.dist-info (METADATA only) first on PYTHONPATH of an interpreter without xdist, then run `python3 tools/gate_timing.py first-run --suite boundary-push` (says parallel) beside gate.py's unit-tests lane (runs serially).

## Proposed Fix

Read xdist one way everywhere, by what the gate does: `gate_prereqs` reports pytest-xdist present only when its module is importable, so the preflight, the cost line and the gate make one reading.

## Acceptance Criteria

- [ ] **AC1** Given an interpreter carrying pytest-xdist's metadata but no importable xdist module, when the prerequisite check runs, then it names pytest-xdist missing and the cost line says the suite runs serially, as gate.py runs it
  - **Verify:** pytest tools/tests/test_gate_prereqs.py::XdistReadingTests::test_metadata_without_a_module_reads_as_missing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | sdlc-studio | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
