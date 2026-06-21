# CR-0053: autosprint DoD includes documentation + deterministic doc-coverage gate

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Date:** 2026-06-21

## Summary

Comparing the operator's tranche-orchestrator prompt to reference-autosprint: our loop matches/exceeds it on guardrails but DROPPED the documentation discipline. The prompt's DoD requires 'user and operator documentation updated' and 'full lifecycle including documentation - do not bypass any stage'. Our conformance stages (decomposed->AC->tested->verified->reconciled->critiqued) have no documented stage - which is why the self-audit found pvd/provenance/telemetry/skill-update shipping with no help-catalogue entry. Add documentation to the DoD, enforced deterministically.

## Acceptance Criteria

- [x] conformance gains a 'documented' stage; a unit cannot reach Done with its user/operator docs un-updated
- [x] a deterministic doc-coverage check flags any Type-Reference command or scripts/ script lacking a help-catalogue + reference entry; wired into the gate (the check that would have caught the audit gap)
- [x] reference-autosprint DoD updated to require docs, a structured final report (actioned/rejected/blocked/assumptions/decisions-ref/attention), and a Phase-1 'batch all clarifying questions' step
- [x] unit-tested; independent critic APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
