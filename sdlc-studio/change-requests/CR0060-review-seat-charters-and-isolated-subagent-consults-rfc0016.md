# CR-0060: Review-seat charters and isolated-subagent consults RFC0016 lean

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

Implements RFC0016's accepted lean core: review SEATS (the Three Amigos + PM/PO owners) become
structured **charters** consulted as **isolated subagents** with a synthesis step, reusing the
existing ledgers as the externalised record. The declined tail (broker tier, detection envelope,
ratified canon) is the external authored-identity system and is NOT built. Also clears the stale
pre-RFC0017 persona fields still embedded in the consult prompts.

## Acceptance Criteria

- [x] new `templates/personas/review-seat-charter.md` - charter schema (role/mandate, lens,
  non-negotiables, pushes-back-when, mandatory shadow, authority, reads, tensions, disposition)
- [x] `reference-consult.md` uses the charter fields (no pre-RFC0017 goals/concerns/decision-driver/
  red-flag fields remain), runs each seat as an isolated subagent, with an explicit synthesis step
- [x] verdicts recorded via the existing `critic.py` / `ledger.py` (record outside, stance inside)
- [x] `reference-workflow-personas.md` distinguishes review seats (charters) from Cooper design personas
- [x] no broker / detection / canon machinery (declined tail); lint + anchors clean

## Implementation

New `review-seat-charter.md` template; `reference-consult.md` single-persona workflow, the
Consultation Prompt Template, and Team Review all rewritten to the charter model + isolated
subagents + synthesis (RFC0016 D7: surface both on conflict). `reference-workflow-personas.md`
notes the seat-vs-design-persona distinction. Reuses critic.py/ledger.py - no new scripts.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (RFC0016) | Created via `new` (deterministic) |
