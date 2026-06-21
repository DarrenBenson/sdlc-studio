# CR-0055: gate gains a duplicate-id check + optional provenance registration

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Date:** 2026-06-21

## Summary

Self-audit: gate.py does not detect duplicate artifact ids, and reconcile.detect_type keys rows into a dict by normalised id so a second US0001 row silently overwrites the first -> zero drift -> gate false PASS. Add a duplicate-id check (reuse next_id duplicate detection) as a blocking gate check. Optionally register provenance in the gate with blocking=provenance.enforce (the opt-in pattern constitution already uses).

## Acceptance Criteria

- [ ] gate flags duplicate ids in any index as a blocking failure (false-pass closed)
- [ ] optional: provenance registered in the gate, blocking only when provenance.enforce
- [ ] tested with a duplicate-id fixture; critic APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
