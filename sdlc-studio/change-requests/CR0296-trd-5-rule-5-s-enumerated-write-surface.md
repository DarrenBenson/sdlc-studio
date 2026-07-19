# CR-0296: TRD §5 rule 5's enumerated write surface omits at least five shipped committed-workspace writers, one of which (persona_gen.py) the TRD's own ADR-009 describes writing files

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** Medium
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Rule 5 presents itself as the write-surface contract, enumerating nine writers. Confirmed missing: retro.py (`atomic_write` of the committed VELOCITY.md that §6 itself documents as committed), handoff.py (retro Handoff section, handoff index, worklist), archive.py (rewrites _index.md and archive files), `persona_gen.py` (seat/stakeholder cards - and ADR-009 four hundred lines later says `persona_gen.py` 'writes fresh named individuals into personas/seats/'), and decisions.py (the committed ledger, also lockless - filed separately). Per LL0013, a contract that enumerates its write surface silently exempts every writer it forgot: an auditor using rule 5 as the checklist of what may mutate the workspace would clear a tree in which five un-listed mutators run. BG0008 (closed) fixed the same enumeration for `verify_ac`/lessons.py only, confirming the project treats an incomplete rule 5 as a real defect. Verified 3x.

## Impact

Rule 5 presents itself as the write-surface contract, enumerating nine writers.

## Acceptance Criteria

- [ ] Rule 5's writer list includes retro.py, handoff.py, archive.py, `persona_gen.py` and decisions.py, each with its tested boundary
- [ ] Or the rule is restated as non-exhaustive with a pointer to the authoritative writer census, and ADR-009's description no longer contradicts §5

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
