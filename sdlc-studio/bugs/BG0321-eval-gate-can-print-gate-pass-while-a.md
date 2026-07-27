# BG0321: Eval gate can print 'gate pass' while a forbidden behaviour was observed - forbidden behaviours are unrecordable

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/eval_run.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

All 8 scenarios declare `forbidden_behaviours` and `cmd_setup` prints them as grading criteria, but `cmd_record` rejects any --behaviour not in `expected_behaviours` and `cmd_report` counts only expected-behaviour fails - a grader who watched the worker do the forbidden thing cannot make the gate fail through the tool, and the summary still prints 'gate pass'.

## Steps to Reproduce

Evidence (`cmd_record` (lines 84-87), `cmd_report` (lines 104-131), `cmd_setup` (lines 72-73)): `cmd_record` builds known only from `expected_behaviours` and returns 2 on anything else; `cmd_report` iterates expected ids only; grep confirms all 8 scenario files carry `forbidden_behaviours`; the same function was hardened against the sibling ungraded-scenario gap.

## Proposed Fix

Accept forbidden-behaviour ids in `cmd_record` (verdict observed = fail at the declared severity) and make `cmd_report` fail the gate whenever any forbidden behaviour is recorded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
