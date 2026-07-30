# BG0321: Eval gate can print 'gate pass' while a forbidden behaviour was observed - forbidden behaviours are unrecordable

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/eval_run.py, tools/tests/test_eval_run.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

All 8 scenarios declare `forbidden_behaviours` and `cmd_setup` prints them as grading criteria, but `cmd_record` rejects any --behaviour not in `expected_behaviours` and `cmd_report` counts only expected-behaviour fails - a grader who watched the worker do the forbidden thing cannot make the gate fail through the tool, and the summary still prints 'gate pass'.

## Steps to Reproduce

Evidence (`cmd_record` (lines 84-87), `cmd_report` (lines 104-131), `cmd_setup` (lines 72-73)): `cmd_record` builds known only from `expected_behaviours` and returns 2 on anything else; `cmd_report` iterates expected ids only; grep confirms all 8 scenario files carry `forbidden_behaviours`; the same function was hardened against the sibling ungraded-scenario gap.

## Proposed Fix

Accept forbidden-behaviour ids in `cmd_record` (verdict observed = fail at the declared severity) and make `cmd_report` fail the gate whenever any forbidden behaviour is recorded.

## Acceptance Criteria

### AC1: a forbidden behaviour is recordable per case

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** `pytest tools/tests/test_eval_run.py::ForbiddenBehaviourTests`, written red before the fix and green after
- **Verified:** yes (2026-07-27, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-27 | Claude Fable 5 | Affects corrected to the fix footprint incl. its test file (BG0343: the filer wrote the evidence location) |
