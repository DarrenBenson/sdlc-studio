# BG0158: Velocity trusts any closed run-state sharing ONE unit with the retro: a carried-over unit attributes a previous run's elapsed to this sprint, even overriding an explicit --elapsed-hours

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a
> **Delivered-by:** claude-opus-4-8

## Summary

US0175's AC says 'a run-state whose batch is not this sprint's is ignored' but never defines membership; retro.py `_elapsed_hours` (500-514) chose the weakest reading - intersection of at least one unit. `run_state` batches are explicitly CUMULATIVE (`run_state.py`:18-22), so a closed run-state left by a previous runner sprint whose batch contains one carried-over unit (the common failed-then-redelivered case) passes the check, and that old run's full start-to-end elapsed becomes THIS sprint's velocity denominator labelled 'run-state' - the exact 43h confounder the docstring says the check prevents. Worse, a matched stale run-state overrides an operator-supplied --elapsed-hours (retro.py:673-675, asserted by test at `test_retro.py`:488). The only mismatch test uses a fully disjoint batch (US9999), so the defence was never validated against the bug it defends (LL0010). Defect in the in-flight US0175 work - fine to file per the brief. Verified 3x.

## Steps to Reproduce

Close a runner sprint leaving a closed run-state whose cumulative batch includes `US_A.` Next interactive sprint redelivers `US_A` among new units and runs retro - `_elapsed_hours` matches on the one-unit intersection and reports the OLD run's full elapsed as this sprint's denominator, overriding any --elapsed-hours supplied.

## Proposed Fix

Strengthen the match: require the run-state batch to substantially cover the retro's units (subset/majority rule) or match on run identity/date window rather than any-intersection; never let a matched run-state override an explicit --elapsed-hours; add a carried-over-one-unit regression test alongside the disjoint case.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
