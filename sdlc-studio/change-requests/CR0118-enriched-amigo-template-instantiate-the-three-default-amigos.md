# CR-0118: Enriched amigo template + instantiate the three default amigos (Cooper depth + seat discipline)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

RFC0020 D4 made concrete. The Three Amigos seats ship today as a blank, review-only charter (templates/personas/review-seat-charter.md) - thin on the things that make an expert useful (no goals, proficiency, behaviour, scenario). Fuse the Cooper goal-directed depth (Who They Are, Craft Goals, Proficiency, Frustrations, Scenario from persona-template.md) with the seat discipline (Mandate, Non-Negotiables, Shadow, Tensions, Authority) into a single enriched amigo card with a DUAL RENDER (a build/author render + a review render, used by separate instances per the independence gate). Ship an amigo-template.md plus three instantiated default amigos (Engineering, QA, Product) at this depth, so projects start with genuinely useful amigos rather than placeholders and can specialise from there (the D7 practitioner-persona shape).

## Acceptance Criteria

- [x] templates/personas/amigo-template.md exists: Cooper-depth sections (Who They Are, Craft Goals, Proficiency, Frustrations, Scenario) + seat-discipline sections (Non-Negotiables, Pushes Back When, Shadow, Tensions, Authority) + an explicit dual-render note (build/author vs review, separate instances)
- [x] three default amigos are instantiated at that depth: Engineering, QA, Product - named, specific, with real proficiency + a Shadow each, not placeholders
- [x] the contract stays law (a Non-Negotiable: expertise serves the file-list/ACs/gates, never overrides) and green stays the oracle (QA amigo never judges green); documented in reference-workflow-personas.md
- [x] lint + gate green (British English, no em-dash, no provenance tags); CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
