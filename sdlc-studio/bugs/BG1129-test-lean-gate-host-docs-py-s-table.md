# BG1129: test_lean_gate_host_docs.py's table test says a hook honouring a value other than 1 fails it, but an edit outside the lines `_hook_code` cuts passes it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_gate_host_docs.py, changelog.d/BG1129.md
> **Evidence:** BG1095 QA review, qa-seat-BG1095-r1, 2026-10-26, at ed8cf5e9: the one new finding, with H6 confirmed in isolation.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T12:10:32Z

## Summary

BG1095's QA review (APPROVE, 2026-10-26). The docstring at tools/tests/`test_lean_gate_host_docs.py`:172-175 says a hook 'honouring a value other than 1' fails the table test. That holds only for edits inside the lines `_hook_code` cuts from .githooks/pre-push. Mutant H6, inserting `[ -n "${SDLC_GATE_LOCAL:-}" ] && on_host=""` just before the host-branch header (pre-push:233), makes the gate run on this machine with a host set and `SDLC_GATE_LOCAL`=yes, contradicting row 3 of both tables, and this test and `test_remote_gate_push.py` both stay green.

## Steps to Reproduce

Apply H6 to .githooks/pre-push and run tools/tests/`test_lean_gate_host_docs.py` and tools/tests/`test_remote_gate_push.py`: green.

## Proposed Fix

Either narrow the docstring to edits inside the cut, or make `_hook_code` refuse an `on_host` assignment outside its cut so H6 fails.

## Acceptance Criteria

- [ ] **AC1** Given H6 applied to .githooks/pre-push, then the table test fails, or its docstring no longer claims that case
  - **Verify:** pytest tools/tests/test_lean_gate_host_docs.py::GateHostDocsTests::test_an_on_host_override_outside_the_cut_is_caught

## Impact

A test docstring claims a protection the test does not give.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
