# BG0500: the runbook guard runs in no gate lane, so the runbook can rot between tool-suite runs

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional
> **Affects:** tools/runbook.py, .githooks/pre-commit, package.json, tools/tests/test_runbook.py
> **Evidence:** Found by the independent closing-review pass on US0613 during the RUN-01KYZKY5 close.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`tools/runbook.py` enforces the sprint-toolchain runbook's step order, its per-step command coverage and its verb freshness. It appears in neither `.githooks/pre-commit` nor `package.json`, so it runs only when the whole tools suite runs. AGENTS.md names the pre-commit lane roster and this guard is absent from it. That is LL0027 exactly - a gate belongs in the command people actually run, not in the step they are told to run - and the runbook is the document AGENTS.md now tells every agent to read before each sprint step.

## Steps to Reproduce

Grep `.githooks/` and `package.json` for `runbook`: no match. The guard therefore never runs on a commit that edits the runbook.

## Proposed Fix

Add it as a pre-commit lane, diff-scoped to the runbook file so it costs nothing on unrelated commits, and extend the lane-roster pinning in tools/tests/`test_check_spec_claims.py.`

## Acceptance Criteria

- [x] A commit that blanks a runbook step's command column is refused by the pre-commit gate, and the lane roster in AGENTS.md names the guard.

## Impact

A commit can reorder the runbook's steps, blank a step's command column or leave a rotted verb behind, and the gate stays green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
