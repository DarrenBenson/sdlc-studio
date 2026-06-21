# CR-0059: Persona well-formedness check cast-role-aware advisory RFC0017 WS3

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

Implements RFC0017 WS3 (D4 = advisory): a deterministic, cast-role-aware well-formedness check
for goal-directed personas. `validate.py personas` scans `sdlc-studio/personas/*.md` and flags a
persona missing a section for its cast role. Advisory only - it never blocks (a persona is a
design aid; a draft is legitimate) and is not in the hard gate. The dogfood learning is honoured:
the Negative variant (no Experience Goals; Why-not + Scenario) is accepted, and Customer/Served
make Experience Goals + Scenario optional.

## Acceptance Criteria

- [x] `validate.py personas` reports each persona missing a section for its cast role (advisory; exits 0)
- [x] cast-role-aware: the Negative variant (Why-not, no Experience Goals) and Customer/Served
  (Experience and Scenario optional) are not false-flagged; a missing cast role is itself flagged
- [x] no-op when there is no personas dir; `index.md` skipped; surfaced via `persona review`
- [x] tested; dogfood-clean on sdlc-studio's own Maya (Primary) and Trevor (Negative)

## Implementation

Added `check_personas(root)` + `cmd_personas` + the `personas` subcommand to `validate.py`
(mirroring the existing non-artifact `instructions` check), with `_persona_cast_role` /
`_headings` / `_present` helpers. Documented in `reference-persona.md` (well-formed section +
`persona review` step). Advisory by design - resolves RFC0017 D4.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (RFC0017) | Created via `new` (deterministic) |
