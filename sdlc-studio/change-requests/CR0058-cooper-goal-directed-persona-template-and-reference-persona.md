# CR-0058: Cooper goal-directed persona template and reference-persona model RFC0017 WS1

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

Implements RFC0017 WS1: replace the old enhanced-persona template and the two-category model
with Alan Cooper's goal-directed model. A persona is a specific, goal-led design target; the
deliverable is a well-formed persona file. No research/evidence apparatus and no authored-identity
machinery (RFC0017 scope) - a goal-directed persona is merely good input to an external identity
system (RFC0016), not something sdlc-studio compiles.

## Acceptance Criteria

- [x] `templates/personas/persona-template.md` is the Cooper schema: cast role, a specific named
  individual, ordered End goals, Experience goals, behaviours and context, frustrations, a scenario
- [x] `reference-persona.md` defines the full cast (Primary/Secondary/Supplemental/Negative/
  Customer/Served), the End + Experience goal model, and "well-formed file" as the bar
- [x] design personas (Cooper cast) are distinguished from review seats (Three Amigos -> RFC0016)
- [x] no research/evidence apparatus, no identity compiler (scope honoured); lint + gate green

## Implementation

Rewrote `templates/personas/persona-template.md` to the Cooper goal-directed schema. Updated
`reference-persona.md`: the two-category model became the cast + goal model (anchor `#categories`
preserved), the Required Sections table became the well-formed Cooper schema, and the archetype
seeds are labelled as review-seat (RFC0016) seeds, distinct from the design cast.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (RFC0017) | Created via `new` (deterministic) |
