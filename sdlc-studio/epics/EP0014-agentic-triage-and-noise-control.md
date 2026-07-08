# EP0014: Agentic triage and noise control

> **Status:** Ready
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new

## Summary

Moves the human from gate to auditor: triage becomes explicit, agent-performable status
transitions with a human sampling policy (all Critical items, a configurable share of the
rest, plus every raiser/triager severity disagreement), triage-quality metrics that justify
the sampling rate, and built-in noise controls (individual artefacts for Medium+, Low
findings consolidated, a per-session creation cap). Also records orchestrator-allocated
tranche membership in the ledger without becoming a scheduler. Groups CR0173 (agentic triage
workflow), CR0172 (tranche reference field). Depends on EP0012 (stable ids) and CR0169
(structured `triaged_by`).

## Story Breakdown

- [ ] [US0065: Triage status vocabulary and gated transitions recording triaged_by](../stories/US0065-triage-status-vocabulary-and-gated-transitions-recording-triaged.md)
- [ ] [US0066: Human sampling policy and triage-quality metrics](../stories/US0066-human-sampling-policy-and-triage-quality-metrics.md)
- [ ] [US0067: Triage noise controls: Medium-plus individual, Low consolidated, session cap](../stories/US0067-triage-noise-controls-medium-plus-individual-low-consolidated.md)
- [ ] [US0068: Optional tranche reference field, record-only](../stories/US0068-optional-tranche-reference-field-record-only.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
