# CR-0011: PRD Plan-file lifecycle Location omits its backing script scripts/plan.py

> **Status:** Complete
> **Priority:** Low
> **Type:** Improvement
> **Requester:** Project Audit
> **Date:** 2026-06-20
> **Affects:** prd.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The Feature Inventory convention is to name the backing script per row, but the Plan-file lifecycle row omits scripts/plan.py, leaving a shipped, tested script untraced.

## Problem

prd.md:122-127 states the Location column names the deterministic script that backs the command. prd.md:143 'Plan-file lifecycle' lists only reference-plan-files.md with no script, though scripts/plan.py backs it (docstring 'Claude Code plan-file manager') and is unit-tested (test_plan.py). plan.py is the only script-backed feature missing its script reference.

## Proposed Changes

### Item 1: PRD Plan-file lifecycle Location omits its backing script scripts/plan.py

**Priority:** Low **Effort:** TBD

Update prd.md:143 Location cell to 'reference-plan-files.md, scripts/plan.py' to match the documented convention and restore code-to-spec traceability.

## Impact Assessment

### Existing Functionality

plan.py is an unmapped deterministic script: a code-to-PRD reconcile cannot tie it to any feature row even though it is shipped and tested.

## Acceptance Criteria

- [x] Update prd.md:143 Location cell to 'reference-plan-files.md, scripts/plan.py' to match the documented convention and restore code-to-spec tr

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: prd) |
