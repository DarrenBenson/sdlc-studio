# CR-0218: the converged seat home: retire amigos/ precedence, one layout, upgrade offers generation first

> **Status:** Complete
> **Verification depth:** functional - red-then-green across both delivery rounds. Round 1: a declared-role seat beats the legacy amigos file (the old order was proven inverted by a red test), legacy fallback warns with the migration path, `--apply` migrates amigos/ to seats/ mechanically without overwriting an existing seat filename, and is idempotent; suite 1591. Round 2, on two late-found defects: the role-collision skip including its post-apply resolution assertion, and the CLI decline gate driven through `main()`; the critic re-ran both repros live plus a two-legacy-cards-one-role probe; suite 1632 green.
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

RFC0028/RFC0021 D2: prerequisite of team generation (Dani, blocking). `persona_resolve` prefers personas/amigos/ over seats/, and every upgraded project carries generic cards there - a generated team would be silently shadowed forever. Converge on seats/ as the runtime home; reconcile the validator layout model, reference-persona-generate Output Format, and the generator write paths in one unit (Sam objection 7); the upgrade flow offers team generation BEFORE, and suppresses, the default-amigo install.

## Acceptance Criteria

- [x] `persona_resolve` resolves seats/ as the primary project home; a role-claiming personas/amigos/ card is detected and migrated/retired with an explicit report (never silently shadowed), including under --dry-run
- [x] project upgrade offers team generation before the default-amigo install and suppresses the install when the offer is taken; declining installs defaults as today
- [x] `check_personas` validates the seats/ and stakeholders/ layout without emitting the persona-layout warning for the generator's canonical output; reference-persona-generate Output Format matches the real write paths

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
