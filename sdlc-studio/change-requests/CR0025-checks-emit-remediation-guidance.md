# CR-0025: deterministic checks emit remediation guidance, not just findings

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** scripts/lib/sdlc_md.py (hint registry), scripts/conformance.py, scripts/integrity.py, scripts/audit.py, scripts/reconcile.py
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The deterministic checks report **findings** (what is wrong) but no **remediation**
(what to do) or **interpretation** (which kind of problem). A fresh consuming
project runs `conformance` and gets "575 not conformant" with no idea whether that
is a parser bug, an unadopted discipline, or real drift (the agent-crew BG0020
experience). Add a shared remediation layer to all four checks: a per-finding fix
hint + a bulk-pattern interpretation.

## Problem

`status hint` already gives "the single next action", but conformance / integrity /
audit / reconcile emit raw counts. The operator must already know the skill to act
on them, which defeats the point on a new project.

## Proposed Changes

### Item 1: Shared remediation hint registry

**Priority:** High **Effort:** Low

A `REMEDIATION` registry in `lib/sdlc_md.py` mapping each check's finding-kind to a
one-line fix hint, plus `remediation_lines(check, kinds)` returning the hints for
the kinds present (stable order). One source, reused by every check.

### Item 2: Guidance in each check's text output

**Priority:** High **Effort:** Medium

`conformance`, `integrity`, `audit`, `reconcile` print a `Guidance:` block (text
mode; JSON stays pure data) listing the fix hints for the finding-kinds present.
`conformance` also prints a bulk-pattern note: when most units miss the same stage,
say "looks like an unadopted discipline / template shape, not per-unit drift."

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| lib/sdlc_md.py | REMEDIATION registry + remediation_lines | New |
| conformance/integrity/audit/reconcile | Guidance block in text output | Modified |

### Breaking Changes

None. JSON output is unchanged (additive guidance is text-only).

## Acceptance Criteria

- [x] `remediation_lines(check, kinds)` returns the registered fix hint for each finding-kind present, in stable order, and nothing for absent kinds.
- [x] Each of conformance/integrity/audit/reconcile prints a `Guidance:` block in text mode listing the hints for the findings present; JSON output is unchanged.
- [x] conformance prints a bulk-pattern note when most units miss the same stage (discipline-vs-drift interpretation).
- [x] Unit-tested for the registry and for each check's guidance output.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (remediation) | Complete - US0022: shared REMEDIATION registry + Guidance in all 4 checks + bulk note; critic-approved (added registry-completeness contract test) |
| 2026-06-20 | Darren Benson | Raised - a check should tell the operator what to do, not just what is wrong (agent-crew wall-of-red) |
